#!/usr/bin/env python3
"""
cloner.py – Clone, update, package, and serve websites for offline use.

NEW COMMANDS
============
    update      Safely refresh an existing offline repo with changes from live site.
    savewcof    Bundle a local clone into a single .wcof archive (ZIP under the hood).
    runwcof     Launch a temporary server from a .wcof archive.

USAGE
=====
    # Clone (unchanged)
    webcloner clone https://example.com ./offline_copy --depth 2

    # Update
    webcloner update https://example.com ./offline_copy

    # Package to one‑file
    webcloner savewcof mysite.wcof ./offline_copy

    # Serve the packaged file
    webcloner runwcof mysite.wcof 8000

DEPENDENCIES
============
    pip install requests beautifulsoup4 tqdm flask
"""
import argparse
import pathlib
import re
import shutil
import sys
import tempfile
import urllib.parse
import zipfile
from collections import deque
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

###########################################################################
# Helper utilities
###########################################################################

def _safe_path(url_path: str) -> pathlib.Path:
    """Convert URL path to a safe relative filesystem path."""
    if url_path.endswith('/') or url_path == '':
        url_path += 'index.html'
    url_path = re.sub(r'[?#].*$', '', url_path.lstrip('/'))
    return pathlib.Path(url_path)


def _write_binary(content: bytes, dest: pathlib.Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)


def _write_text(text: str, dest: pathlib.Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding='utf-8', errors='ignore')

###########################################################################
# Clone (and internal crawler)
###########################################################################

def clone_site(start_url: str, out_dir: pathlib.Path, max_depth: int = 2):
    session = requests.Session()
    parsed_root = urllib.parse.urlparse(start_url)
    root_domain = parsed_root.netloc

    queue = deque([(start_url, 0)])
    seen = set()
    progress = tqdm(unit='file')

    while queue:
        url, depth = queue.popleft()
        if url in seen or depth > max_depth:
            continue
        seen.add(url)
        progress.set_description(f"[{depth}] {url}")

        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
        except Exception as exc:
            progress.write(f"⚠️  Failed to fetch {url}: {exc}")
            continue

        path = _safe_path(urllib.parse.urlparse(url).path)
        dest = out_dir / path
        content_type = resp.headers.get('content-type', '')
        is_html = content_type.startswith('text/html')

        if is_html:
            soup = BeautifulSoup(resp.text, 'html.parser')
            assets = []
            for tag, attr in [('a', 'href'), ('link', 'href'), ('img', 'src'), ('script', 'src')]:
                for el in soup.find_all(tag):
                    link = el.get(attr)
                    if not link:
                        continue
                    abs_url = urllib.parse.urljoin(url, link)
                    parsed = urllib.parse.urlparse(abs_url)
                    if parsed.netloc != root_domain:
                        continue
                    assets.append((abs_url, depth + 1))
                    el[attr] = _safe_path(parsed.path).as_posix()
            queue.extend(assets)
            _write_text(str(soup), dest)
        else:
            _write_binary(resp.content, dest)

        progress.update(1)

    progress.close()
    print(f"\n✅ Finished! Saved {len(seen)} files to {out_dir.resolve()}")

###########################################################################
# Update logic – clone to a temp dir then sync changed files
###########################################################################

def update_site(start_url: str, repo_dir: pathlib.Path, depth: int = 2):
    if not repo_dir.exists():
        sys.exit(f"❌ Repo {repo_dir} does not exist. Clone first.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        print("🔄 Cloning latest version to temporary directory…")
        clone_site(start_url, tmp_path, max_depth=depth)

        print("📂 Syncing changes back to repo…")
        for src in tmp_path.rglob('*'):
            if src.is_dir():
                continue
            rel = src.relative_to(tmp_path)
            dst = repo_dir / rel
            if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        print("✅ Update complete.")

###########################################################################
# Package to .wcof (zip) and run from .wcof
###########################################################################

def save_wcof(filename: str, dest_dir: pathlib.Path, repo_dir: pathlib.Path):
    """Package repo_dir into dest_dir/filename (.wcof ZIP)"""
    if not repo_dir.exists():
        sys.exit(f"❌ Repo {repo_dir} does not exist.")
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / (filename if filename.endswith('.wcof') else filename + '.wcof')

    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in repo_dir.rglob('*'):
            if file.is_file():
                zf.write(file, file.relative_to(repo_dir))
    size_kb = out_path.stat().st_size / 1024
    print(f"📦 Saved {repo_dir} → {out_path} ({size_kb:.0f} KB)")


def run_wcof(wcof_path: pathlib.Path, host: str = '0.0.0.0', port: int = 5000):
    if not wcof_path.exists():
        sys.exit(f"❌ File {wcof_path} not found.")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        with zipfile.ZipFile(wcof_path, 'r') as zf:
            zf.extractall(tmp_dir)
        print(f"📂 Extracted to {tmp_dir}")
        run_server(tmp_dir, host=host, port=port)

###########################################################################
# Flask server reuse
###########################################################################

def run_server(root_dir: pathlib.Path, host: str = '0.0.0.0', port: int = 5000):
    from flask import Flask, send_from_directory, abort

    if not root_dir.exists():
        sys.exit(f"❌ Directory {root_dir} does not exist.")

    app = Flask(__name__, static_folder=str(root_dir), static_url_path='')

    @app.route('/', defaults={'req_path': 'index.html'})
    @app.route('/<path:req_path>')
    def serve(req_path):
        file_path = root_dir / req_path
        if file_path.is_file():
            return send_from_directory(root_dir, req_path)
        index_path = file_path / 'index.html'
        if index_path.is_file():
            return send_from_directory(root_dir, f"{req_path}/index.html")
        return abort(404)

    print(f"🚀 Serving {root_dir.resolve()} at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

###########################################################################
# CLI
###########################################################################

def main():
    parser = argparse.ArgumentParser(description='WebCloner – offline site toolkit')
    sub = parser.add_subparsers(dest='cmd', required=True)

    # clone
    p_clone = sub.add_parser('clone', help='Clone a live site into a local repo')
    p_clone.add_argument('url')
    p_clone.add_argument('output')
    p_clone.add_argument('--depth', type=int, default=2)

    # run
    p_run = sub.add_parser('run', help='Serve a local repo')
    p_run.add_argument('root')
    p_run.add_argument('port', type=int)
    p_run.add_argument('--host', default='0.0.0.0')

    # update
    p_up = sub.add_parser('update', help='Update an existing repo safely')
    p_up.add_argument('url')
    p_up.add_argument('root')
    p_up.add_argument('--depth', type=int, default=2)

    # savewcof
    p_save = sub.add_parser('savewcof', help='Package repo into .wcof single file')
    p_save.add_argument('filename', help='Name of the .wcof file to create')
    p_save.add_argument('dest', help='Directory where the .wcof will be saved')
    p_save.add_argument('root', help='Directory of the cloned repo to package')

    # runwcof
    p_runw = sub.add_parser('runwcof', help='Serve directly from a .wcof archive')
    p_runw.add_argument('wcof_path')
    p_runw.add_argument('port', type=int)
    p_runw.add_argument('--host', default='0.0.0.0')

    args = parser.parse_args()

    if args.cmd == 'clone':
        clone_site(args.url, pathlib.Path(args.output), args.depth)
    elif args.cmd == 'run':
        run_server(pathlib.Path(args.root), args.host, args.port)
    elif args.cmd == 'update':
        update_site(args.url, pathlib.Path(args.root), args.depth)
    elif args.cmd == 'savewcof':
        save_wcof(
            args.filename,
            pathlib.Path(args.dest),
            pathlib.Path(args.root)
        )
    elif args.cmd == 'runwcof':
        run_wcof(pathlib.Path(args.wcof_path), args.host, args.port)

if __name__ == '__main__':
    main()

