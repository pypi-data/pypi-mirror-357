# File Crud

Simple CRUD operations for files and directories in Python.

# Description

file-crud is a lightweight Python package that provides basic Create, Read, Update, and Delete (CRUD) functions for handling files and directories easily. It includes safe operations with error handling and supports nested directories. Perfect for beginners or simple file management tasks.

The package normalizes file and directory paths across different operating systems (Windows, Linux, macOS), ensuring consistent behavior regardless of how paths are written or used.

# Features

Create a new file with content.

Read the content of a file.

Update (append) content to an existing file.

Delete a file safely with error handling.

Create and delete directories, including nested folders.

Optional recursive deletion: remove directories even if they contain files/subfolders.

Copy and move files with optional overwrite protection.

Copy and move directories recursively with optional overwrite.

Cross-platform path normalization to handle differences between operating systems.

# Installation

```bash
pip install file-crud
```

# Usage

import file_crud as fc #more easy to use

## Create a file

fc.create_file('example.txt', 'Hello, world!') # If you don’t want content, pass None

## Read the file

content = fc.read_file('example.txt')

## Update the file

fc.update_file('example.txt', '\nThis is an added line.') # If no content to add, pass None

## Delete the file

fc.delete_file('example.txt')

## Create a directory (nested paths allowed)

fc.create_directory('my_folder/subfolder')

## Delete a directory (only if empty)

fc.delete_directory('my_folder/subfolder')

## Delete a directory recursively (removes all contents)

fc.delete_directory('my_folder', recursive=True)

## Copy a file (won't overwrite by default)

fc.copy_file('source.txt', 'destination.txt')

## Move a file (won't overwrite by default)

fc.move_file('old_location.txt', 'new_location.txt')

## Copy a directory recursively (won't overwrite by default)

fc.copy_directory('source_folder', 'destination_folder')

## Move a directory recursively (won't overwrite by default)

fc.move_directory('old_folder', 'new_folder')

# Notes on recursive deletion and overwrite

delete_directory with recursive=True removes the entire directory and all its contents — use with caution.

Copy and move functions accept an overwrite parameter (default False) to control whether existing files/directories get overwritten.

# Path Normalization

All functions internally normalize file and directory paths to ensure compatibility across Windows, Linux, and macOS. This means you can use paths with ~, relative paths, or different slash styles, and they will be handled correctly.

# Author

Frank Pineda
Email: fpineda11@gmail.com
