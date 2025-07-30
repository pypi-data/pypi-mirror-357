from setuptools import setup, find_packages

setup(
    name='securehillhell',
    version='0.1',
    author='Durga Maduru',
    author_email='your.email@example.com',
    description='Cryptography examples: Hill cipher and Diffie-Hellman',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
