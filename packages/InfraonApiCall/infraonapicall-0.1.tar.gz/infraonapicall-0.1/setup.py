from setuptools import setup, find_packages

setup(
    name='InfraonApiCall',
    version='0.1',
    packages=find_packages(),
    description='Library to call Infraon API for auth token',
    author='ravikumar',
    install_requires=[
        'requests'
    ],
)
