from setuptools import setup, find_packages

setup(
    name='palworld-api',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.11',
    ],
    python_requires='>=3.11',
    description='A Python API wrapper for the Palworld Rest API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='dkoz',
    author_email='koz@beskor.net',
    url='https://github.com/dkoz/palworld-api',
)
