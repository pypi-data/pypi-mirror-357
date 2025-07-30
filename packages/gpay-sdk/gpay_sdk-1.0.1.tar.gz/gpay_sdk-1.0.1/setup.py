from setuptools import setup, find_packages

setup(
    name='gpay-sdk', 
    version='1.0.1',
    description='GPay API Python Client Library',
    author='Libya Guide for Information Technology and Training',
    author_email='info@libyaguide.net',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    url='https://github.com/Libya-Guide/GPay-Python-SDK',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
