from setuptools import setup, find_packages

setup(
    name='InfraonApiCall',
    version='1',
    description='Library to call Infraon API for auth token',
    author='ravikumar',
    packages=find_packages(),  # ✅ Only include once!
    install_requires=[
        'requests'
    ],
)
