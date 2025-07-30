# file-crud

Simple CRUD operations for files in Python.

## Description

`file-crud` is a lightweight Python package that provides basic Create, Read, Update, and Delete (CRUD) functions for handling files easily. Perfect for beginners or simple file management tasks.

## Features

- Create a new file with content.
- Read the content of a file.
- Update (append) content to an existing file.
- Delete a file safely with error handling.

## Installation

```bash
pip install file-crud
```

## Usage

import file_crud as fc

# Create a file

fc.create('example.txt', 'Hello, world!') (If you don´t want content in the file, put "None")

# Read the file

fc.read('example.txt')

# Update the file

fc.update('example.txt', '\nThis is an added line.') (If you don´t want content in the file, put "None")

# Delete the file

fc.delete('example.txt')

## Author

Frank Pineda
Email: fpineda11@gmail.com
