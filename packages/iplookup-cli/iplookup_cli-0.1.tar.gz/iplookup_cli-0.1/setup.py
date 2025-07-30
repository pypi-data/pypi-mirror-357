from setuptools import setup, find_packages

setup(
    name="iplookup-cli",
    version="0.1",
    author="EletrixTime / eletrix.fr",
    author_email="hey@eletrix.fr",   
    url="https://github.com/eletrixtime/iplookup-cli",  
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'iplookup = iplookup:main',
        ],
    },
    description="CLI for looking up IP adresses",  
    python_requires='>=3.6',
    requires= [
        "requests",
        "colorama"
    ],
    
)
