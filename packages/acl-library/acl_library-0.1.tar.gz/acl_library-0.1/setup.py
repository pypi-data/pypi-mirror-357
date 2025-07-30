from setuptools import setup, find_packages

setup(
    name='acl-library',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.0',
        'djangorestframework',
        'drf-yasg'
        
    ],
)