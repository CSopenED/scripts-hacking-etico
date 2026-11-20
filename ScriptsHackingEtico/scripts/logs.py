#!/usr/bin/env python3
"""Analizador de logs SSH / Apache: detecta intentos de fuerza bruta
y saca las IPs mas activas. Usa logs de tus propios sistemas."""
import os
import re
import shlex
from collections import Counter

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

RE_SSH_FALLO = re.compile(r"Failed password.*from (\d{1,3}(?:\.\d{1,3}){3})")
RE_SSH_INVALIDO = re.compile(r"Invalid user \S+ from (\d{1,3}(?:\.\d{1,3}){3})")
RE_SSH_OK = re.compile(r"Accepted (?:password|publickey).*from (\d{1,3}(?:\.\d{1,3}){3})")
RE_APACHE = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3}).*"(?:GET|POST|HEAD) (\S+).*" (\d{3})')


def analizar_ssh(lineas):
    fallos, validos_ok, invalidos = Counter(), Counter(), Counter()
    for linea in lineas:
        m = RE_SSH_FALLO.search(linea)
        if m:
            fallos[m.group(1)] += 1
            continue
        m = RE_SSH_INVALIDO.search(linea)
        if m:
            invalidos[m.group(1)] += 1
            continue
        m = RE_SSH_OK.search(linea)
        if m:
            validos_ok[m.group(1)] += 1
    return fallos, invalidos, validos_ok


def analizar_apache(lineas):
    ips, rutas_sospechosas, codigos = Counter(), Counter(), Counter()
    sospechosas = ("wp-login", "wp-admin", ".env", ".git", "phpmyadmin", "xmlrpc.php",
                   "..%2f", "etc/passwd", "union+select", "<script")
    for linea in lineas:
        m = RE_APACHE.match(linea)
        if not m:
            continue
        ip, ruta, codigo = m.groups()
        ips[ip] += 1
        codigos[codigo] += 1
        if any(s in ruta.lower() for s in sospechosas):
            rutas_sospechosas[(ip, ruta)] += 1
    return ips, rutas_sospechosas, codigos


def main():
    print(f"{C}{B}=== ANALIZADOR DE LOGS ==={X}")
    print("Usa logs de tus propios sistemas (SSH o Apache/Nginx).\n")
    raw = input("Ruta al archivo de log: ").strip()
    if not raw:
        return
    try:
        ruta = os.path.expanduser(shlex.split(raw)[0])
    except ValueError:
        ruta = raw.strip("'\"")
    if not os.path.isfile(ruta):
        print(f"{R}No encuentro el archivo: {ruta}{X}")
        return

    with open(ruta, "r", errors="replace") as f:
        lineas = f.readlines()
    print(f"Leyendo {len(lineas)} lineas...\n")

    es_ssh = any("sshd" in l or "Failed password" in l or "Invalid user" in l for l in lineas[:500])

    if es_ssh:
        fallos, invalidos, ok = analizar_ssh(lineas)
        print(f"{B}Tipo detectado: log de SSH{X}\n")
        print(f"{B}Top IPs con contraseñas fallidas:{X}")
        for ip, n in fallos.most_common(10):
            marca = f"  {R}<- posible fuerza bruta{X}" if n >= 10 else ""
            print(f"  {R if n >= 10 else Y}{n:>5}{X}  {ip}{marca}")
        if invalidos:
            print(f"\n{B}Top IPs probando usuarios inexistentes:{X}")
            for ip, n in invalidos.most_common(10):
                print(f"  {Y}{n:>5}{X}  {ip}")
        if ok:
            print(f"\n{B}Inicios de sesion correctos:{X}")
            for ip, n in ok.most_common(10):
                print(f"  {G}{n:>5}{X}  {ip}")
        total_fallos = sum(fallos.values())
        print(f"\n{B}Resumen: {total_fallos} intentos fallidos, {len(fallos)} IPs distintas, "
              f"{len(ok)} accesos correctos{X}")
    else:
        ips, rutas_sosp, codigos = analizar_apache(lineas)
        print(f"{B}Tipo detectado: log de servidor web (Apache/Nginx){X}\n")
        print(f"{B}Top IPs por numero de peticiones:{X}")
        for ip, n in ips.most_common(10):
            marca = f"  {R}<- trafico muy alto{X}" if n >= 200 else ""
            print(f"  {C}{n:>5}{X}  {ip}{marca}")
        print(f"\n{B}Codigos de respuesta:{X}")
        for cod, n in sorted(codigos.items()):
            color = G if cod.startswith("2") else (Y if cod.startswith("4") else R)
            print(f"  {color}{cod}{X}  {n}")
        if rutas_sosp:
            print(f"\n{R}{B}Peticiones a rutas sensibles (posible escaneo/ataque):{X}")
            for (ip, ruta_), n in rutas_sosp.most_common(15):
                print(f"  {R}[{n}]{X} {ip}  ->  {ruta_}")
        else:
            print(f"\n{G}No se detectaron rutas sensibles conocidas.{X}")

    print(f"\n{Y}Nota: muchos intentos no siempre significan un ataque en curso, "
          f"pero merece revisión si no los reconoces.{X}")


if __name__ == "__main__":
    main()
