from clima import obtener_clima
from gemini_ai import preguntar_ia
from rich import print
from datetime import datetime
import memory
import random
import os

def registrar_evento(evento):
    with open("eventos.txt", "a") as archivo:
        hora = datetime.now().strftime("%H:%M:%S")
        archivo.write(f"[{hora}] {evento}\n")

def saludar():
    respuestas = [
        "Buenas tardes, Jean.",
        "A sus ordenes, Jefe.",
        "Sistema operativo y listo para ayudar.",
        "Me alegra verlo nuevamente.",
        "Saludos, Jean"
    ]
    return "[bold green]" + random.choice(respuestas) + "[/bold green]"

def estado_sistema():
    respuestas = [
        "Todos los modulos operativos.",
        "Sistemas estable.",
        "Memoria activa.",
        "Nucleo funcionando correctamente.",
        "Diagnostico completo. Sin errores."
    ]
    return random.choice(respuestas)

def procesar_comando(comando):
    comando = comando.lower()

    if comando == "hola":
        return saludar()

    elif comando == "quien eres":
        return "soy SIATD IA"

    elif comando == "ayuda":
        return "hola, quien eres, ayuda, estado, hora, fundador, salir"

    elif comando == "estado":
        return "SIATD IA operativo al 100%"

    elif comando == "estado de sistema":
        return estado_sistema()

    elif comando == "hora":
        ahora = datetime.now()
        return "hora actual: " +  ahora.strftime("%H:%M:%S")

    elif comando == "fundador":
        return "Mi creador es Jean Franco"

    elif comando.startswith("recuerda"):
        try:
            _, clave, valor = comando.split(" ", 2)
            memory.guardar(clave, valor)
            return "guardado correctamente"
        except:
            return "uso: recuerda clave valor"

    elif comando.startswith("dime"):
        try:
            _, clave = comando.split(" ", 1)
            return memory.obtener(clave)
        except:
            return "uso: dime clave"
    elif comando.startswith("registrar"):
            try:
                _, evento = comando.split(" ", 1)
                registrar_evento(evento)
                return "evento registrado correctamente"
            except:
                return "uso: registrar evento"
    elif comando == "ver eventos":
        if not os.path.exists("eventos.txt"):
            return "no hay eventos registrados"
        with open ("eventos.txt", "r") as archivo:
            contenido = archivo.read()
            if contenido.strip() == "":
                return "no hay eventos registrados"
            return contenido

    elif comando.startswith("clima "):
        ciudad = comando.replace("clima ", "").strip()
        return obtener_clima(ciudad)

    elif comando == "salir":
        return "salir"

    else:
        return preguntar_ia(comando)
