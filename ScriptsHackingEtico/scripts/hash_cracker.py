#!/usr/bin/env python3
"""Identificador de hashes + cracker por diccionario.
Para practicar con hashes de retos CTF o tus propias pruebas, nunca con
hashes de cuentas ajenas."""
import hashlib
import os
import shlex
import time

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

HASHES = {32: ["md5"], 40: ["sha1"], 56: ["sha224"], 64: ["sha256"],
          96: ["sha384"], 128: ["sha512"]}
COMUNES = ["123456", "password", "12345678", "qwerty", "abc123", "111111",
           "123456789", "iloveyou", "admin", "welcome", "letmein", "monkey",
           "dragon", "sunshine", "princess", "football", "shadow", "master",
           "login", "passw0rd", "123123", "hola", "contraseña", "test",
           "guest", "root", "toor", "1234", "12345", "qwerty123"]


def calcular(algo, texto):
    try:
        return hashlib.new(algo, texto.encode()).hexdigest()
    except ValueError:
        return None


def identificar(h):
    h = h.strip().lower()
    candidatos = HASHES.get(len(h), [])
    if not all(c in "0123456789abcdef" for c in h):
        return []
    return candidatos


def cargar_diccionario(ruta):
    if not ruta:
        return COMUNES
    if not os.path.isfile(ruta):
        print(f"{Y}No se encontro '{ruta}'; se usa el diccionario basico incluido.{X}")
        return COMUNES
    with open(ruta, "r", errors="replace") as f:
        return [l.strip() for l in f if l.strip()]


def main():
    print(f"{C}{B}=== IDENTIFICADOR Y CRACKER DE HASHES ==={X}")
    print("Solo para hashes de retos CTF o pruebas propias.\n")
    h = input("Hash a analizar: ").strip().lower()
    if not h:
        return

    algos = identificar(h)
    if not algos:
        print(f"{R}No se reconoce el formato (longitud {len(h)}, ¿es hexadecimal?).{X}")
        return
    print(f"\n{G}Longitud {len(h)}: posible {', '.join(algos).upper()}{X}")

    print("\n1) Probar diccionario basico (30 palabras comunes)")
    print("2) Usar mi propio archivo de diccionario")
    op = input("Elige [1]: ").strip() or "1"
    ruta = None
    if op == "2":
        raw = input("Ruta al diccionario (una palabra por linea): ").strip()
        try:
            ruta = os.path.expanduser(shlex.split(raw)[0]) if raw else None
        except ValueError:
            ruta = raw.strip("'\"") or None

    palabras = cargar_diccionario(ruta)
    print(f"\nProbando {len(palabras)} palabras con {algos[0]}...")
    ini = time.time()
    for palabra in palabras:
        if calcular(algos[0], palabra) == h:
            print(f"\n{G}{B}¡Encontrado! El valor original es: {palabra}{X}")
            print(f"({time.time() - ini:.2f} s, {len(palabras)} intentos)")
            return
    print(f"\n{Y}No se encontró en el diccionario ({time.time() - ini:.2f} s). "
          f"Prueba con una lista mas grande (rockyou.txt en entornos de laboratorio).{X}")


if __name__ == "__main__":
    main()
