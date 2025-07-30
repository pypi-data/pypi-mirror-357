from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="webcloner",
    version="1.0.0",
    author="Synthfax",
    author_email="synthfax@gmail.com",  # change to your real or dummy email
    description="Offline website cloner, updater, and packager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Synthfax/WebCloner",
    project_urls={
        "Bug Tracker": "https://github.com/Synthfax/WebCloner/issues",
    },
    packages=find_packages(include=["webcloner", "webcloner.*"]),
    install_requires=[
        "requests>=2.0",
        "beautifulsoup4>=4.0",
        "tqdm>=4.0",
        "flask>=2.0"
    ],
    entry_points={
        "console_scripts": [
            "webcloner=webcloner.cloner:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    license="Apache License 2.0",
    include_package_data=True,
    zip_safe=False,
)
