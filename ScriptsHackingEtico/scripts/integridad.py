#!/usr/bin/env python3
"""Monitor de integridad de archivos: guarda los hashes SHA-256 de una carpeta
y despues avisa de archivos modificados, nuevos o borrados."""
import hashlib
import json
import os
import shlex

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
BASE = os.path.expanduser("~/.integridad")


def hash_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def escanear(carpeta):
    datos = {}
    for raiz, _, archivos in os.walk(carpeta):
        for a in archivos:
            ruta = os.path.join(raiz, a)
            try:
                datos[os.path.relpath(ruta, carpeta)] = hash_archivo(ruta)
            except (OSError, PermissionError):
                pass
    return datos


def fichero_base(carpeta):
    return os.path.join(BASE, hashlib.sha1(carpeta.encode()).hexdigest()[:12] + ".json")


def main():
    print(f"{C}{B}=== MONITOR DE INTEGRIDAD ==={X}")
    print("Arrastra la carpeta a vigilar a esta ventana y pulsa Enter.\n")
    raw = input("Carpeta: ").strip()
    if not raw:
        return
    try:
        carpeta = os.path.abspath(os.path.expanduser(shlex.split(raw)[0]))
    except ValueError:
        carpeta = os.path.abspath(raw.strip("'\""))
    if not os.path.isdir(carpeta):
        print(f"{R}No es una carpeta valida: {carpeta}{X}")
        return

    os.makedirs(BASE, exist_ok=True)
    fb = fichero_base(carpeta)
    existe = os.path.exists(fb)
    print("\n1) Crear linea base (foto del estado actual)")
    print(f"2) Comprobar cambios {'' if existe else '(aun no hay linea base)'}")
    op = input("Elige: ").strip()

    if op == "1":
        datos = escanear(carpeta)
        with open(fb, "w") as f:
            json.dump(datos, f)
        print(f"\n{G}Linea base guardada: {len(datos)} archivos.{X}")
    elif op == "2" and existe:
        with open(fb) as f:
            antes = json.load(f)
        ahora = escanear(carpeta)
        mod = [k for k in ahora if k in antes and ahora[k] != antes[k]]
        nuevos = [k for k in ahora if k not in antes]
        borrados = [k for k in antes if k not in ahora]
        for k in mod: print(f"  {Y}[MODIFICADO]{X} {k}")
        for k in nuevos: print(f"  {C}[NUEVO]{X}      {k}")
        for k in borrados: print(f"  {R}[BORRADO]{X}    {k}")
        if not (mod or nuevos or borrados):
            print(f"\n{G}Todo intacto: no hay cambios.{X}")
    else:
        print(f"{R}Opcion no valida o falta la linea base.{X}")


if __name__ == "__main__":
    main()
