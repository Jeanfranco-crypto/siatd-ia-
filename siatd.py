import core
import os
import re
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def jarvis_hablar(texto_rich):
    #1. Filtramos las etiquetas de Rich para que la voz no las intente deletrear
    texto_limpio = re.sub(r'\[.*?]', '',texto_rich)

    #2. Reemplazamos los saltos de Linea por espacios
    texto_limpio = texto_limpio.replace('\n', ' ').strip()

    #3. Lanzamos espeak calibrado estilo Jarvis (voz grave y ritmo pausado)
    if texto_limpio:
        os.system(f"espeak -v es -s 155 -p 40 '{texto_limpio}' 2>/dev/null")

# Limpieza inicial de la terminal antes de arrancar la grabacion
os.system('clear' if os.name == 'posix' else 'cls')

console.print(Panel("[bold cyan] SIATD IA v1.5 - PROTOCOLO JARVIS INTEGRADO [/bold cyan]", subtitle="Acceso Autorizado - Jean Franco", expand=False))

# Saludo de arranque automatico en voz alta
saludo_inicial = "todos los sistemas principales en linea y optimizados, Jefe, esperando sus instrucciones."
console.print(f'[bold cyan]{saludo_inicial}[/bold cyan]')
jarvis_hablar(saludo_inicial)


while True:

    try:

        # Prompt interactivo estilo consola avanzada
        comando = console.input("\n[bold cyan]JARVIS_SYSTEM[/bold cyan] [bold white]>[/bold white] ")

        if not comando.strip():
            continue

        respuesta = core.procesar_comando(comando)

        if respuesta == "salir":
           despedida = "Desactivando nucleos del sistema y guardando registros. Hasta luego, Jefe"
           console.print(f"[bold red]{despedida}[/bold red]")
           jarvis_hablar(despedida)
           break

        elif respuesta == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')
            jarvis_hablar("Pantalla restablecida, Jefe.")
            continue

        # Muestra en pantalla el formato Rich y Jarvis habla
        console.print(respuesta)
        jarvis_hablar(respuesta)

    except KeyboardInterrupt:
        despedida_forzada = "\nInterrupcion detectada. Cerrando sistemas de forma segura, Jefe."
        console.print(f"[bold red]{despedida_forzada}[/bold red]")
        jarvis_hablar(despedida_forzada)
        sys.exit()
