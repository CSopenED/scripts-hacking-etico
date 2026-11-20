#!/usr/bin/env python3
"""Comprobador de contrasenas: calcula la entropia y consulta Have I Been Pwned
con k-anonimato (solo se envian 5 caracteres del hash, nunca la contrasena)."""
import getpass
import hashlib
import math
import ssl
import urllib.request

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
COMUNES = {"123456", "password", "12345678", "qwerty", "abc123", "111111", "123456789",
           "iloveyou", "admin", "welcome", "contraseña", "password1", "letmein"}


def entropia(pw):
    pool = 0
    if any(c.islower() for c in pw): pool += 26
    if any(c.isupper() for c in pw): pool += 26
    if any(c.isdigit() for c in pw): pool += 10
    if any(not c.isalnum() for c in pw): pool += 33
    return len(pw) * math.log2(pool) if pool else 0


def filtraciones(pw):
    sha = hashlib.sha1(pw.encode()).hexdigest().upper()
    prefijo, resto = sha[:5], sha[5:]
    req = urllib.request.Request(f"https://api.pwnedpasswords.com/range/{prefijo}",
                                 headers={"User-Agent": "ComprobadorPassword/1.0"})
    with urllib.request.urlopen(req, timeout=10, context=ssl.create_default_context()) as r:
        for linea in r.read().decode().splitlines():
            h, n = linea.split(":")
            if h == resto:
                return int(n)
    return 0


def main():
    print(f"{C}{B}=== COMPROBADOR DE CONTRASEÑAS ==={X}")
    print("No se muestra ni se guarda lo que escribas.\n")
    pw = getpass.getpass("Contraseña a comprobar: ")
    if not pw:
        return

    e = entropia(pw)
    if pw.lower() in COMUNES:
        nivel, col = "MUY DEBIL (es de las mas usadas)", R
    elif e < 40:
        nivel, col = "DEBIL", R
    elif e < 60:
        nivel, col = "ACEPTABLE", Y
    elif e < 80:
        nivel, col = "BUENA", G
    else:
        nivel, col = "EXCELENTE", G
    print(f"\n  Longitud: {len(pw)}   Entropia: {e:.0f} bits")
    print(f"  Fortaleza: {col}{B}{nivel}{X}")

    print("\nConsultando Have I Been Pwned...")
    try:
        n = filtraciones(pw)
        if n:
            print(f"  {R}{B}Aparece en {n:,} filtraciones. No la uses.{X}")
        else:
            print(f"  {G}No aparece en filtraciones conocidas.{X}")
    except Exception as err:
        print(f"  {Y}No se pudo consultar (¿sin internet?): {err}{X}")
    print("\nConsejo: una frase larga de 4+ palabras al azar gana a una clave corta con simbolos.")


if __name__ == "__main__":
    main()
