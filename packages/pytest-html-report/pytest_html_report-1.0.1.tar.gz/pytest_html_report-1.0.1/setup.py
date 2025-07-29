from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytest-html-report",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Enhanced HTML reporting for pytest with categories, specifications, and detailed logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pytest-html-report",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytest>=6.0",
        "pyyaml>=5.3",
        "beautifulsoup4>=4.9",
    ],
    entry_points={
        "pytest11": [
            "pytest_html_report = pytest_html_report.plugin",
        ],
    },
)