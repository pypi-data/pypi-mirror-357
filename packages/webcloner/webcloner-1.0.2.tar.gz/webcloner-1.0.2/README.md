# WebCloner

*Clone, update, package & serve websites for offline use – all from one tiny Python script.*

---

**Made by Synthfax**

---

## Features

| Command      | What it does                                                                       |
| ------------ | ---------------------------------------------------------------------------------- |
| **clone**    | Recursively downloads a live site to a local folder and rewrites internal links.   |
| **run**      | Fires up a lightweight Flask web server that serves a cloned repo.                 |
| **update**   | Refreshes an existing repo *safely* by cloning into a temp dir and syncing changes |
| **savewcof** | Bundles an entire repo into a single `.wcof` archive (ZIP under the hood).         |
| **runwcof**  | Serves a `.wcof` file directly – no manual extraction required.                    |

Additional features:

* **Progress bars** via *tqdm* so you’re never in the dark.
* **Domain‑locked crawling** – stays on the origin host.
* **Depth limiter** so you don’t mirror the whole internet by accident.
* **Pure‑Python** – works on Windows, macOS & Linux (incl. WSL & Termux).

---

## Requirements

* Python ≥ 3.8
* The following packages (installed automatically via pip):

  * `requests`
  * `beautifulsoup4`
  * `tqdm`
  * `flask`

---

## Installation

### 🔌 Install via pip (recommended)

```bash
python -m pip install webcloner
```

*(Use `python3` instead of `python` if needed.)*

---

## Quick Start

```bash
# 1. Clone a website (max 2 levels deep)
webcloner clone https://example.com ./offline_copy --depth 2

# 2. Serve the local copy in your browser
webcloner run ./offline_copy 8000

# 3. Package the local copy into a single .wcof file
webcloner savewcof mysite.wcof ./offline_copy

# 4. Serve directly from a .wcof archive
webcloner runwcof mysite.wcof 8080
```

---

## Command Reference

### `clone`

```
webcloner clone <url> <output_dir> [--depth N]
```

* `url` – starting URL (with http\:// or https\://).
* `output_dir` – local folder for files.
* `--depth` – recursion depth (default 2).

Downloads and rewrites same-domain links for offline use.

---

### `run`

```
webcloner run <repo_dir> <port> [--host 0.0.0.0]
```

Serves the cloned site via Flask.

---

### `update`

```
webcloner update <url> <repo_dir> [--depth N]
```

Safely refreshes the repo by syncing changes from the live site.

---

### `savewcof`

```
webcloner savewcof <filename.wcof> <dest_dir> <repo_dir>
```

Bundles the repo into a `.wcof` ZIP archive.

---

### `runwcof`

```
webcloner runwcof <file.wcof> <port> [--host 0.0.0.0]
```

Extracts and serves from a `.wcof` archive on the fly.

---

## FAQ

| Question                              | Answer                                                               |
| ------------------------------------- | -------------------------------------------------------------------- |
| *Why does it download external CDNs?* | Only same-domain links are crawled. Some CSS/JS may load CDN assets. |
| *Can I clone login-required sites?*   | Not yet. You’d need to add cookies manually in the script.           |
| *Is JavaScript executed?*             | No. This is a static grabber, no JS rendering.                       |

---

## License

Licensed under the **Apache License 2.0** – see [LICENSE](LICENSE) for full terms.