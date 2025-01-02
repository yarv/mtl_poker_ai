from setuptools import setup, find_packages

setup(
    name="poker_game",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'tk',
        'pillow',
        'numpy',
        'cairosvg',
    ],
) 