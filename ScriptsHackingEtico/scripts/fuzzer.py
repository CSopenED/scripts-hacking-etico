#!/usr/bin/env python3
"""Fuzzer de directorios: prueba una lista de rutas comunes contra una web
y muestra cuales existen. Usa solo contra tu propia web o una VM de
laboratorio (DVWA, Juice Shop, etc.)."""
import ipaddress
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

RUTAS = [
    "admin", "login", "wp-admin", "wp-login.php", "phpmyadmin", "backup",
    "backup.zip", "config.php", ".env", ".git/config", "robots.txt",
    "sitemap.xml", "api", "api/v1", "test", "dev", "uploads", "images",
    "server-status", "README.md", "composer.json", "package.json",
    ".htaccess", "web.config", "admin.php", "db.sql", "dump.sql",
    "console", "actuator", "debug", "swagger.json", "graphql",
]


def es_privada(host):
    try:
        ip = socket.gethostbyname(host)
        a = ipaddress.ip_address(ip)
        return a.is_private or a.is_loopback
    except (socket.gaierror, ValueError):
        return False


def probar(base, ruta):
    url = urllib.parse.urljoin(base, ruta)
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "FuzzerDirectorios/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ssl.create_default_context()) as r:
            return ruta, r.status, len(r.read(2000))
    except urllib.error.HTTPError as e:
        return ruta, e.code, 0
    except Exception:
        return None


def main():
    print(f"{C}{B}=== FUZZER DE DIRECTORIOS ==={X}")
    print("Usa esto solo contra tu propia web o una VM de laboratorio (DVWA, Juice Shop).\n")
    base = input("URL base (ej. http://localhost:8080/): ").strip()
    if not base:
        return
    if not base.startswith(("http://", "https://")):
        base = "http://" + base
    if not base.endswith("/"):
        base += "/"

    host = urllib.parse.urlparse(base).hostname or ""
    if not es_privada(host):
        print(f"\n{Y}{B}AVISO:{X} '{host}' no parece una direccion local/privada.")
        print("Hacer fuzzing contra una web que no es tuya puede ser ilegal sin autorizacion.")
        if input("Escribe SI para confirmar que tienes autorizacion: ").strip() != "SI":
            print("Cancelado.")
            return

    print(f"\nProbando {len(RUTAS)} rutas contra {base} ...\n")
    with ThreadPoolExecutor(max_workers=20) as ex:
        resultados = [r for r in ex.map(lambda r: probar(base, r), RUTAS) if r]

    encontrados = [r for r in resultados if r[1] not in (404,)]
    if not encontrados:
        print(f"{Y}Ninguna de las rutas probadas devolvio una respuesta distinta de 404.{X}")
        return

    for ruta, status, tam in sorted(encontrados, key=lambda x: x[1]):
        if status == 200:
            color = G
        elif status in (301, 302, 403):
            color = Y
        else:
            color = C
        print(f"  {color}[{status}]{X}  /{ruta:<22} {tam} bytes")

    print(f"\n{B}{len(encontrados)} rutas con respuesta de {len(RUTAS)} probadas{X}")
    print(f"{Y}Un 200 o 403 en 'admin', '.env' o 'backup.zip' merece revision inmediata.{X}")


if __name__ == "__main__":
    main()
