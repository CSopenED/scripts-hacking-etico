#!/usr/bin/env python3
"""Honeypot sencillo: abre un puerto falso (parece SSH) y registra quien conecta.
Solo escucha y guarda lo que recibe; no ejecuta nada. Para laboratorio propio."""
import os
import socket
import threading
import time

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
LOG = os.path.expanduser("~/honeypot_log.txt")
lock = threading.Lock()


def registrar(linea):
    with lock:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(linea + "\n")


def atender(conn, addr):
    ip, puerto = addr
    hora = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n")
        conn.settimeout(5)
        datos = conn.recv(200).decode(errors="replace").strip().replace("\n", " ")
    except Exception:
        datos = ""
    finally:
        conn.close()
    linea = f"{hora} | {ip}:{puerto} | recibido: {datos!r}"
    print(f"{R}[ALERTA]{X} {linea}")
    registrar(linea)


def main():
    print(f"{C}{B}=== HONEYPOT ==={X}")
    entrada = input("Puerto a vigilar (Enter = 2222): ").strip() or "2222"
    if not entrada.isdigit() or not (1024 < int(entrada) < 65536):
        print(f"{R}Usa un puerto entre 1025 y 65535 (asi no hace falta sudo).{X}")
        return
    puerto = int(entrada)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", puerto))
    except OSError as e:
        print(f"{R}No se pudo abrir el puerto {puerto}: {e}{X}")
        return
    srv.listen(20)
    print(f"\n{G}Escuchando en el puerto {puerto}.{X} Registro en: {LOG}")
    print(f"Prueba desde otra pestana del terminal:  nc localhost {puerto}")
    print("Pulsa Ctrl+C para parar.\n")
    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=atender, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print(f"\n{Y}Honeypot detenido.{X}")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
