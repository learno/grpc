try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='GRPC',
    version='0.1',
    description='A socket RPC bases on Gevent',
    author='Learno',
    author_email='learncpp@gmail.com',
    url='http://code.google.com/p/grpc/',
    packages=['grpc'],
    install_requires=['gevent'],
    classifiers=[
    "License :: oSI Approved :: MIT License",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules"],
 )
