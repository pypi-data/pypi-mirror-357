import numpy as np

def hola(nombre):
    return f"Hola, {nombre}!"

class Saludo:
    def __init__(self):
        print('Hola, te saludo desde Saludo.__init__')

def generar_array(numeros):
    return np.arange(numeros)


if __name__ == '__main__':
    print(generar_array(5))
    
