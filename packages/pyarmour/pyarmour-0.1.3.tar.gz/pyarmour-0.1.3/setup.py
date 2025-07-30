from setuptools import setup, find_namespace_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import os
import sys

# Add src directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Version
VERSION = "0.1.3"

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Add any post-installation steps here

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # Add any post-development steps here

class PostEggInfoCommand(egg_info):
    """Post-egg-info for development mode."""
    def run(self):
        egg_info.run(self)
        # Add any post-egg-info steps here

setup(
    name="pyarmour",
    version=VERSION,
    author="PyArmour Team",
    author_email="team@pyarmour.com",
    description="Zero-configuration adversarial robustness testing for ML models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyarmour/pyarmour",
    project_urls={
        "Bug Tracker": "https://github.com/pyarmour/pyarmour/issues",
        "Documentation": "https://pyarmour.readthedocs.io",
        "Source": "https://github.com/pyarmour/pyarmour"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Topic :: Software Development :: Testing"
    ],
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "click>=8.1.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
            "pre-commit>=3.3.3",
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.2.0",
            "numpydoc>=1.5.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "pyarmour=pyarmour.cli:cli",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
        "egg_info": PostEggInfoCommand
    },
    include_package_data=True,
    zip_safe=False,
    keywords=["adversarial", "machine learning", "security", "testing", "numpy"],
    license="MIT",
    platforms=["any"]
)
