from setuptools import setup, find_packages
from pathlib import Path

# Load README.md as long description
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")
setup(
    name="astro_what",
    version="0.1.3",
    description="CLI astronomy toolkit for moon data and lunar phases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shreenidhi",
    packages=find_packages(),
    install_requires=[
        "click",
        "skyfield",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "astro=astro_what.cli:cli"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)
