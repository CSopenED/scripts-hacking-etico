#!/usr/bin/env python3
"""Navaja suiza para CTF: codifica/decodifica base64, hex, binario, URL, ROT13,
cifrado Cesar (con fuerza bruta) e identifica tipos de hash por longitud."""
import base64
import binascii
import codecs
import urllib.parse

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

HASHES = {32: "MD5 / NTLM", 40: "SHA-1", 56: "SHA-224", 64: "SHA-256",
          96: "SHA-384", 128: "SHA-512"}


def cesar(texto, n):
    out = []
    for c in texto:
        if c.isalpha():
            base = ord("A") if c.isupper() else ord("a")
            out.append(chr((ord(c) - base + n) % 26 + base))
        else:
            out.append(c)
    return "".join(out)


def ejecutar(op, t):
    if op == "1": return base64.b64encode(t.encode()).decode()
    if op == "2": return base64.b64decode(t + "=" * (-len(t) % 4)).decode(errors="replace")
    if op == "3": return t.encode().hex()
    if op == "4": return bytes.fromhex(t.replace(" ", "")).decode(errors="replace")
    if op == "5": return " ".join(f"{b:08b}" for b in t.encode())
    if op == "6": return bytes(int(b, 2) for b in t.split()).decode(errors="replace")
    if op == "7": return urllib.parse.quote(t)
    if op == "8": return urllib.parse.unquote(t)
    if op == "9": return codecs.encode(t, "rot_13")
    if op == "10":
        return "\n".join(f"  Desplazamiento {n:>2}: {cesar(t, n)}" for n in range(1, 26))
    if op == "11":
        s = t.strip()
        if all(c in "0123456789abcdefABCDEF" for c in s) and len(s) in HASHES:
            return f"Longitud {len(s)}: posible {HASHES[len(s)]}"
        if s.startswith(("$2a$", "$2b$", "$2y$")): return "Posible bcrypt"
        if s.startswith("$6$"): return "Posible SHA-512 crypt (Linux)"
        if s.startswith("$1$"): return "Posible MD5 crypt"
        return "No se reconoce el formato"


MENU = """
 1) Base64 codificar      2) Base64 decodificar
 3) Hex codificar         4) Hex decodificar
 5) Binario codificar     6) Binario decodificar
 7) URL codificar         8) URL decodificar
 9) ROT13                10) Cesar (fuerza bruta, 25 opciones)
11) Identificar hash      0) Salir
"""


def main():
    print(f"{C}{B}=== DECODIFICADOR PARA CTF ==={X}")
    while True:
        print(MENU)
        op = input("Elige: ").strip()
        if op in ("0", ""):
            return
        if op not in [str(i) for i in range(1, 12)]:
            print(f"{R}Opcion no valida{X}")
            continue
        texto = input("Texto: ")
        try:
            print(f"\n{G}{B}Resultado:{X}\n{ejecutar(op, texto)}")
        except (binascii.Error, ValueError) as e:
            print(f"{R}Entrada no valida para esta operacion: {e}{X}")


if __name__ == "__main__":
    main()
