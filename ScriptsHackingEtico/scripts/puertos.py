#!/usr/bin/env python3
"""Escaner de puertos TCP multihilo con lectura de banners.
Uso: solo en tu equipo, tu red o con autorizacion expresa."""
import ipaddress
import socket
import time
from concurrent.futures import ThreadPoolExecutor

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

COMUNES = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
           1433, 1723, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443, 27017]


def probar(host, puerto):
    try:
        with socket.create_connection((host, puerto), timeout=0.8) as s:
            banner = ""
            try:
                s.settimeout(0.8)
                if puerto in (80, 8000, 8080):
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                datos = s.recv(150).decode(errors="ignore").strip()
                if datos:
                    banner = datos.splitlines()[0][:80]
            except Exception:
                pass
            return puerto, banner
    except Exception:
        return None


def es_privada(ip):
    try:
        a = ipaddress.ip_address(ip)
        return a.is_private or a.is_loopback
    except ValueError:
        return False


def main():
    print(f"{C}{B}=== ESCANER DE PUERTOS ==={X}")
    objetivo = input("Objetivo (Enter = 127.0.0.1): ").strip() or "127.0.0.1"
    try:
        ip = socket.gethostbyname(objetivo)
    except socket.gaierror:
        print(f"{R}No se pudo resolver '{objetivo}'{X}")
        return

    if not es_privada(ip):
        print(f"\n{Y}{B}AVISO:{X} {ip} es una IP publica. Escanear sistemas ajenos sin permiso")
        print("puede ser delito. Solo sigue si es tuyo o tienes autorizacion escrita.")
        if input("Escribe SI para confirmar que tienes autorizacion: ").strip() != "SI":
            print("Cancelado.")
            return

    print("\n1) Puertos comunes (rapido)\n2) Puertos 1-1024\n3) Puertos 1-10000")
    op = input("Elige [1]: ").strip() or "1"
    puertos = COMUNES if op == "1" else range(1, 1025) if op == "2" else range(1, 10001)

    print(f"\nEscaneando {objetivo} ({ip})...\n")
    ini = time.time()
    with ThreadPoolExecutor(max_workers=200) as ex:
        res = [r for r in ex.map(lambda p: probar(ip, p), puertos) if r]

    for puerto, banner in sorted(res):
        try:
            serv = socket.getservbyport(puerto)
        except OSError:
            serv = "desconocido"
        extra = f"  {banner}" if banner else ""
        print(f"  {G}[ABIERTO]{X} {puerto:<6} {serv:<12}{extra}")
    if not res:
        print(f"  {Y}No se encontraron puertos abiertos.{X}")
    print(f"\n{B}{len(res)} abiertos en {time.time() - ini:.1f} s{X}")


if __name__ == "__main__":
    main()
