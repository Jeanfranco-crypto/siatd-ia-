import json
import os

ARCHIVO = "memoria.json"

# cargar memoria desde archivo
if os.path.exists(ARCHIVO):
    with open(ARCHIVO, "r") as f:
        memoria = json.load(f)

else:
    memoria = {}

def guardar(clave, valor):
    memoria[clave] = valor

    with open(ARCHIVO, "w") as f:
        json.dump(memoria, f)

def obtener(clave):
    return memoria.get(clave, "no tengo ese dato")
