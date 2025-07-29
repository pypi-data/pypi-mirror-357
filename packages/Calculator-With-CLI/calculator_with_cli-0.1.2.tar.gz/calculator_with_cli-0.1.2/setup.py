from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for PyPI long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='Calculator_With_CLI',
    version='0.1.2',  # Bump version to re-upload
    description='A simple calculator package with CLI support',
    long_description=long_description,
    long_description_content_type='text/markdown',  # <- this tells PyPI to render markdown
    author='Ahmed',
    author_email='ahmed.mca18@gmail.com',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'calculator = calculator_cli.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
