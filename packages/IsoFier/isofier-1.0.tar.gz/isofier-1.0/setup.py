from setuptools import setup, find_packages

setup(
    name='IsoFier',
    version='1.0',
    packages=find_packages(),
    install_requires=['pycdlib'],
    author='bowser-2077',
    description='Create ISO files from directories or single files',
    python_requires='>=3.0',
)
