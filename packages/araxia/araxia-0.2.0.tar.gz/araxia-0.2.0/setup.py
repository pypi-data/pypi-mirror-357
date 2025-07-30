# setup.py
from setuptools import setup, find_packages

setup(
    name='araxia',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
    ],
    author='C5m7b4',
    description='A simple from-scratch neural network time series forecaster with preprocessing utilities.',
    url='https://github.com/C5m7b4/Araxia',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
