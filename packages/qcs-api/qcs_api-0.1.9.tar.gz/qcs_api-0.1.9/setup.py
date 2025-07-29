from setuptools import setup, find_packages

setup(
    name='qcs_api', 
    version='0.1.9', 
    packages=find_packages(), 
    install_requires=[
        'requests',
    ],
    author='TUM QCS', 
    classifiers=['Programming Language :: Python :: 3', ],
)

