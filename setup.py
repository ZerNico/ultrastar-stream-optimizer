from setuptools import setup, find_packages

setup(
    name="usoptimize",
    description="A Python CLI UltraStar Song Converter to optimize files for the web.",
    version="0.1",
    author="Nico Franke <nico.franke01@gmail.com>",
    packages=find_packages(),
    install_requires=[
        "tqdm==4.64.0",
        "chardet==3.0.4",
        "ffmpeg-python==0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "usoptimize = usoptimize.cli:cli"
        ]
    },
)