import os
from setuptools import setup, find_packages

setup(
    name='upnp_forwarder',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'miniupnpc',
    ],
    author='Your Name', # Replace with your name
    description='A Python package for UPnP port forwarding',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/upnp_forwarder', # Replace with your project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Or your preferred license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
