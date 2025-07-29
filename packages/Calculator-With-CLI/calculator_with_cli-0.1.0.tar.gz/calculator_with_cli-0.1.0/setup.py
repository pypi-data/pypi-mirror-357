from setuptools import setup, find_packages

setup(
    name='Calculator_With_CLI',
    version='0.1.0',
    description='A simple calculator package with CLI support',
    author='Ahmed',
    author_email='ahmed.mca18@gmail.com',
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if needed
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
