from setuptools import setup, find_packages

setup(
    name="echothreads",
    packages=find_packages(where="src") + ["scripts"],
    version = "0.3.3",
    py_modules=["main"],
    package_dir={
        "": "src",
        "scripts": "scripts",
        "LoreWeave": "src/loreweave",
    },
    install_requires=[
        "redis",
        "pyyaml",
        "matplotlib",
        "requests",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "loreweaver=main:cli",
        ],
    },
    package_data={
        "": ["*.yaml", "*.json"],
    },
    include_package_data=True,
    author="Your Name",
    author_email="your.email@example.com",
    description="A system that transforms code changes into narratives, capturing the essence and intention of each commit.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jgwill/EchoThreads",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
