import re

from setuptools import find_packages, setup

# Read version from pyproject.toml
with open("pyproject.toml", "r", encoding="utf-8") as f:
    content = f.read()
    version_match = re.search(r'version\s*=\s*"(.*?)"', content)
    if not version_match:
        raise ValueError("Could not find version string in pyproject.toml")
    VERSION = version_match.group(1)

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scarf-sdk",
    version=VERSION,
    author="Scarf",
    author_email="engineering@scarf.sh",
    description="Python bindings for Scarf telemetry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scarf-sh/scarf-py",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
        ],
    },
)
