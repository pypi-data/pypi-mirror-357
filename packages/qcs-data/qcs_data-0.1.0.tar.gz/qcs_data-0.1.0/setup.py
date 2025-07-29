from setuptools import setup, find_packages

setup(
    name='qcs_data', 
    version='0.1.0', 
    packages=find_packages(), 
    install_requires=[
        'requests',
    ],
    author='TUM QCS', 
    classifiers=['Programming Language :: Python :: 3', ],
)

