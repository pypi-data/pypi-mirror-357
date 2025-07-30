import os
import shutil

def normalize_path(path):
    """Normaliza la ruta según el sistema operativo actual."""
    return os.path.normpath(os.path.expanduser(path))

# ----- Archivos -----

def create_file(name, content):
    if content is None:
        content = ''
    path = normalize_path(name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_file(name):
    path = normalize_path(name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def update_file(name, content):
    path = normalize_path(name)
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        print('File updated successfully.')
    except FileNotFoundError:
        print('File not found')
    except Exception as e:
        print(f'Error while running the program. {e}')

def delete_file(name):
    path = normalize_path(name)
    try:
        os.remove(path)
        print('File deleted successfully.')
    except FileNotFoundError:
        print('File not found')
    except Exception as e:
        print(f'Error while running the program. {e}')

# ----- Directorios -----

def create_directory(name):
    path = normalize_path(name)
    try:
        os.makedirs(path, exist_ok=True)
        print(f'Directory created: {path}')
    except Exception as e:
        print(f'Error while running the program. {e}')


def delete_directory(name, recursive=False):
    path = normalize_path(name)
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        print(f'Directory deleted: {path}')
    except Exception as e:
        print(f'Error while running the program. {e}')

# ----- Copiar y mover archivos/directorios -----

def copy_file(src, dest, overwrite=False):
    src_path = normalize_path(src)
    dest_path = normalize_path(dest)
    try:
        if not os.path.isfile(src_path):
            print(f"[ERROR] Source file does not exist: {src_path}")
            return False
        if os.path.exists(dest_path) and not overwrite:
            print(f"[ERROR] Destination file already exists: {dest_path}")
            return False
        shutil.copy2(src_path, dest_path)
        print(f"File copied from {src_path} to {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error copying file: {e}")
        return False

def move_file(src, dest, overwrite=False):
    src_path = normalize_path(src)
    dest_path = normalize_path(dest)
    try:
        if not os.path.isfile(src_path):
            print(f"[ERROR] Source file does not exist: {src_path}")
            return False
        if os.path.exists(dest_path) and not overwrite:
            print(f"[ERROR] Destination file already exists: {dest_path}")
            return False
        shutil.move(src_path, dest_path)
        print(f"File moved from {src_path} to {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error moving file: {e}")
        return False

def copy_directory(src, dest, overwrite=False):
    src_path = normalize_path(src)
    dest_path = normalize_path(dest)
    try:
        if not os.path.isdir(src_path):
            print(f"[ERROR] Source directory does not exist: {src_path}")
            return False
        if os.path.exists(dest_path):
            if overwrite:
                shutil.rmtree(dest_path)
            else:
                print(f"[ERROR] Destination directory already exists: {dest_path}")
                return False
        shutil.copytree(src_path, dest_path)
        print(f"Directory copied from {src_path} to {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error copying directory: {e}")
        return False

def move_directory(src, dest, overwrite=False):
    src_path = normalize_path(src)
    dest_path = normalize_path(dest)
    try:
        if not os.path.isdir(src_path):
            print(f"[ERROR] Source directory does not exist: {src_path}")
            return False
        if os.path.exists(dest_path):
            if overwrite:
                shutil.rmtree(dest_path)  # Aquí elimina la carpeta destino
            else:
                print(f"[ERROR] Destination directory already exists: {dest_path}")
                return False
        shutil.move(src_path, dest_path)
        print(f"Directory moved from {src_path} to {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error moving directory: {e}")
        return False
