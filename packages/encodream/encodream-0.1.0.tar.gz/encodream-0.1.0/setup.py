from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="encodream",
    version="0.1.0",
    author="Eden Simamora",
    author_email="aeden6877@gmail.com",
    description="Encoding Playground of Dreams - ASCII, UTF-8, machine code visualizer & terminal art tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EdenGithhub/encodream",  # Ganti sesuai repo kamu
    project_urls={
        "Documentation": "https://github.com/EdenGithhub/encodream",
        "Source": "https://github.com/EdenGithhub/encodream",
        "Bug Tracker": "https://github.com/EdenGithhub/encodream/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
        "Environment :: Console",
        "Intended Audience :: Developers",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "matplotlib",
        "colorama",
        "pyfiglet",
        "pandas",
        "rich",
        "tqdm",
        "click",
        "tabulate",
        "termcolor",
        "chardet",
        "emoji",
        "faker",
        "markdownify",
        "unidecode",
        "humanize",
        "pyperclip",
        "Pillow",
        "validators",
        "yaspin",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "encodream=encodream.core:main",
        ],
    },
)
