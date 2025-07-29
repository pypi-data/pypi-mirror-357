from setuptools import setup, find_packages

setup(
    name='qcs_data', 
    version='0.1.1', 
    packages=find_packages(), 
    install_requires=[
        'requests',
    ],
    author='TUM QCS', 
    classifiers=['Programming Language :: Python :: 3', ],
)

