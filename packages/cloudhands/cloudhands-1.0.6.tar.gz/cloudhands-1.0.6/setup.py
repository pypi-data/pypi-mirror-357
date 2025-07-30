from setuptools import setup, find_packages
import os
import re

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "cloudhands", "version.py")
    with open(version_file, "r") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="cloudhands",
    version=get_version(),
    author="Cloudhands, Inc.",
    description="Python SDK for CloudHands API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license_files=[],  # Disable automatic license detection
)