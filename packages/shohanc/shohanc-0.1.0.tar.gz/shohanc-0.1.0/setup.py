from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="shohanc",
    version="0.1.0",
    author="Shohan",
    author_email="shohan.dev.cse@gmail.com",
    description="⚡ Ultra-fast Python queue system with native C backend support, persistence, and encryption.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shohan-dev/Shohanc-pypi-libary",  # Replace with your real repo
    packages=find_packages(include=["shohanc", "shohanc.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.0",
        "typing-extensions; python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "build",
            "twine",
        ]
    },
    entry_points={
        "console_scripts": [
            # Example CLI entry (adjust if needed)
            "ultraqueue-cli=shohanc.cli:main"
        ]
    },
    license="MIT",
    keywords="queue performance c-backend encryption persistence fast scalable",
    zip_safe=False,
)
