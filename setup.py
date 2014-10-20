import os

from setuptools import setup, find_packages


requires = [
    'arrow>=0.4.4'
]


setup(name='nativeview',
    version='0.0',
    description='nativeview',
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Arthur Aminov',
    author_email='',
    url='',
    packages=find_packages('nativeview'),
    zip_safe=False,
    install_requires=requires,
)
