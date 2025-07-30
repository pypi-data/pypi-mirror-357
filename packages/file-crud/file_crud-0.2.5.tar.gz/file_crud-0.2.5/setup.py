from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='file-crud',
    version='0.2.5',
    packages=find_packages(),
    description='Simple CRUD operations for file handling in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',  # si usas README.md en Markdown
    author='Frank Pineda',
    author_email='fpineda11@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
