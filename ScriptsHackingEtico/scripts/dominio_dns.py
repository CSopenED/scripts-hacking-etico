#!/usr/bin/env python3
"""Resumen de un dominio: WHOIS basico, DNS y proteccion de correo (SPF y DMARC).
Usa informacion publica. Ideal para auditar tus propios dominios."""
import shutil
import subprocess

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"


def dig(tipo, nombre):
    r = subprocess.run(["dig", "+short", "+time=3", "+tries=1", tipo, nombre],
                       capture_output=True, text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def main():
    print(f"{C}{B}=== RESUMEN DE DOMINIO ==={X}")
    if not shutil.which("dig"):
        print(f"{R}No se encuentra 'dig' en este sistema.{X}")
        return
    dominio = input("Dominio (ej. tuweb.com): ").strip().lower()
    dominio = dominio.replace("https://", "").replace("http://", "").split("/")[0]
    if not dominio:
        return

    print(f"\n{B}Registros DNS{X}")
    for tipo in ("A", "AAAA", "NS", "MX"):
        for v in dig(tipo, dominio) or ["-"]:
            print(f"  {tipo:<5} {v}")

    txt = dig("TXT", dominio)
    print(f"\n{B}Proteccion del correo{X}")
    spf = [t for t in txt if "v=spf1" in t]
    print(f"  {G}[OK] SPF: {spf[0]}{X}" if spf else f"  {R}[FALTA] SPF{X}")
    if spf and spf[0].strip('"').endswith("+all"):
        print(f"  {R}[!] SPF con +all permite que cualquiera envie correo por ti{X}")

    dmarc = [t for t in dig("TXT", f"_dmarc.{dominio}") if "v=DMARC1" in t]
    if dmarc:
        print(f"  {G}[OK] DMARC: {dmarc[0]}{X}")
        if "p=none" in dmarc[0]:
            print(f"  {Y}[!] Politica p=none: solo vigila, no bloquea suplantaciones{X}")
    else:
        print(f"  {R}[FALTA] DMARC{X}")

    if shutil.which("whois"):
        print(f"\n{B}WHOIS (resumen){X}")
        salida = subprocess.run(["whois", dominio], capture_output=True, text=True).stdout
        claves = ("registrar:", "creation date", "updated date", "expir", "name server", "status")
        vistos = 0
        for l in salida.splitlines():
            if any(k in l.lower() for k in claves) and vistos < 12:
                print(f"  {l.strip()}")
                vistos += 1
        if not vistos:
            print("  (sin datos publicos: protegido por privacidad/RGPD)")


if __name__ == "__main__":
    main()
