#!/usr/bin/env python3
"""Enumerador de subdominios via certificate transparency (crt.sh) + DNS.
Usa solo tus propios dominios o con autorizacion expresa."""
import json
import re
import socket
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"


def consultar_crtsh(dominio):
    url = f"https://crt.sh/?q=%25.{dominio}&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "EnumeradorSubdominios/1.0"})
    with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
        datos = json.loads(r.read().decode(errors="replace") or "[]")
    subs = set()
    for fila in datos:
        for nombre in fila.get("name_value", "").split("\n"):
            nombre = nombre.strip().lstrip("*.").lower()
            if nombre.endswith(dominio) and re.match(r"^[a-z0-9.\-]+$", nombre):
                subs.add(nombre)
    return subs


def resolver(host):
    try:
        return host, socket.gethostbyname(host)
    except socket.gaierror:
        return host, None


def main():
    print(f"{C}{B}=== ENUMERADOR DE SUBDOMINIOS ==={X}")
    print("Usa solo tus propios dominios o con autorizacion.\n")
    dominio = input("Dominio (ej. tuweb.com): ").strip().lower()
    dominio = dominio.replace("https://", "").replace("http://", "").split("/")[0]
    if not dominio:
        return

    print(f"\nConsultando crt.sh (certificate transparency) para {dominio}...")
    try:
        subs = consultar_crtsh(dominio)
    except urllib.error.URLError as e:
        print(f"{R}No se pudo consultar crt.sh: {e}{X}")
        return
    except Exception as e:
        print(f"{R}Error al procesar la respuesta: {e}{X}")
        return

    subs.add(dominio)
    print(f"{G}{len(subs)} nombres encontrados.{X} Resolviendo DNS...\n")

    with ThreadPoolExecutor(max_workers=30) as ex:
        resultados = list(ex.map(resolver, sorted(subs)))

    vivos = [(h, ip) for h, ip in resultados if ip]
    muertos = [h for h, ip in resultados if not ip]

    print(f"{B}Subdominios que resuelven:{X}")
    for h, ip in sorted(vivos):
        print(f"  {G}[VIVO]{X}  {h:<40} {ip}")
    if muertos:
        print(f"\n{B}Aparecen en certificados pero no resuelven ahora ({len(muertos)}):{X}")
        for h in sorted(muertos)[:20]:
            print(f"  {Y}[-]{X} {h}")
        if len(muertos) > 20:
            print(f"  ... y {len(muertos) - 20} mas")

    print(f"\n{B}Total: {len(vivos)} activos de {len(subs)} encontrados{X}")
    print(f"{Y}Nota: certificate transparency es un registro publico; esto no es un escaneo de red.{X}")


if __name__ == "__main__":
    main()
