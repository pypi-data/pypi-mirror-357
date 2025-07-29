from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="faviconx",
    version="1.0.0",
    author="FaviconX Team",
    author_email="contact@faviconx.dev",
    description="A command-line tool for generating favicons from source images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rapidrabbitsoft/faviconx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Pillow>=10.0.0",
        "click>=8.0.0",
        "cairosvg>=2.7.0",
    ],
    entry_points={
        "console_scripts": [
            "faviconx=faviconx.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=["favicon", "icon", "generator", "cli", "web", "pwa", "apple-touch-icon", "android"],
) 