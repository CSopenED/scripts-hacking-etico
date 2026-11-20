#!/usr/bin/env python3
"""Muestra los metadatos de un archivo (fotos, PDF, documentos) para ver
que informacion filtran: camara, fechas, GPS, autor... Usa tus propios archivos."""
import os
import shlex
import shutil
import subprocess

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
INTERESANTES = ("gps", "latitude", "longitude", "author", "creator", "make", "model",
                "software", "dateTimeOriginal", "creationdate", "lastuser", "title", "device")


def main():
    print(f"{C}{B}=== VISOR DE METADATOS ==={X}")
    print("Arrastra un archivo tuyo a esta ventana y pulsa Enter.\n")
    raw = input("Archivo: ").strip()
    if not raw:
        return
    try:
        ruta = os.path.expanduser(shlex.split(raw)[0])
    except ValueError:
        ruta = raw.strip("'\"")
    if not os.path.isfile(ruta):
        print(f"{R}No encuentro el archivo: {ruta}{X}")
        return

    if shutil.which("exiftool"):
        comando = ["exiftool", ruta]
        print(f"\n{G}Usando exiftool{X}\n")
    elif shutil.which("mdls"):
        comando = ["mdls", ruta]
        print(f"\n{G}Usando mdls (nativo de macOS){X}")
        print("Para mas detalle: brew install exiftool\n")
    else:
        print(f"{R}No hay exiftool ni mdls disponibles.{X}")
        return

    salida = subprocess.run(comando, capture_output=True, text=True).stdout
    avisos = 0
    for linea in salida.splitlines():
        bajo = linea.lower()
        if any(k.lower() in bajo for k in INTERESANTES) and "(null)" not in linea:
            print(f"{Y}{linea}{X}")
            if "gps" in bajo or "latitude" in bajo or "longitude" in bajo:
                avisos += 1
        else:
            print(linea)
    if avisos:
        print(f"\n{R}{B}¡Cuidado! Este archivo contiene ubicacion GPS.{X}")
        print("Antes de compartirlo, borra los metadatos.")
    else:
        print(f"\n{G}No se ven coordenadas GPS en este archivo.{X}")


if __name__ == "__main__":
    main()
