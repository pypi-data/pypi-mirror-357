from setuptools import setup, find_packages

setup(
    name="astro_what",
    version="0.1",
    description="CLI astronomy toolkit for moon data and lunar phases",
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
        "Topic :: Scientific/Engineering :: Astronomy"
    ]
)
