import sys
import re

# Regex para detectar comandos LaTeX con llaves
latex_cmd = re.compile(r'\\[a-zA-Z]+\{')

def linea_tiene_bloque_abierto(linea):
    """
    Determina si una línea deja un bloque LaTeX sin cerrar
    contando llaves.
    """
    balance = 0

    i = 0
    while i < len(linea):
        if linea[i] == '{':
            balance += 1
        elif linea[i] == '}':
            balance -= 1
        i += 1

    return balance > 0


def main():
    texto = sys.stdin.read()
    lineas = texto.splitlines()

    salida = []
    balance_global = 0

    for linea in lineas:
        # Actualizar balance de llaves global
        balance_global += linea.count('{')
        balance_global -= linea.count('}')

        salida.append(linea)

        # Solo añadimos línea extra si NO estamos dentro de un bloque abierto
        if balance_global == 0:
            salida.append('')  # línea en blanco extra

    sys.stdout.write("\n".join(salida) + "\n")


if __name__ == "__main__":
    main()