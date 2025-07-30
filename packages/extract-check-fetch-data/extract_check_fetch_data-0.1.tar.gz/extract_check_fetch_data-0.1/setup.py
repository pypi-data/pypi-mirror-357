from setuptools import setup, find_packages

setup(
    name='extract_check_fetch_data',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'requests',
    ] 
)