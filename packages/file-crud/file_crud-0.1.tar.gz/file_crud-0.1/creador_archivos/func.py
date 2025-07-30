def create(nombre, contenido):
    if contenido is None:
        contenido = ''
    with open(nombre, 'w', encoding='utf-8') as f:
        f.write(contenido)
def read(nombre):
    with open(nombre, 'r', encoding='utf-8') as f:
        return f.read()

def update(nombre, contenido):
    try:
        with open(nombre, 'a', encoding='utf-8') as f:
         f.write(contenido)
         print('File updated successfully.')
    except Exception as e:    
        print(f'Error while running the program. {e}')

def delete(nombre):
    import os
    try:
        os.remove(nombre)
        print('File deleted successfully.')
    except FileNotFoundError:
        print('File not found')
    except Exception as e:
        print(f'Error while running the program. {e}')