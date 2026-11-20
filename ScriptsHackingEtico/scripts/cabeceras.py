#!/usr/bin/env python3
"""Auditor de cabeceras HTTP de seguridad.
Uso: solo en webs tuyas o con autorizacion expresa."""
import ssl
import urllib.error
import urllib.request

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"

# (cabecera, nombre corto, para que sirve)
CHECKS = [
    ("strict-transport-security", "HSTS", "Obliga al navegador a usar HTTPS"),
    ("content-security-policy", "CSP", "Frena XSS e inyecciones de contenido"),
    ("x-frame-options", "X-Frame-Options", "Evita el clickjacking"),
    ("x-content-type-options", "X-Content-Type-Options", "Evita el MIME sniffing"),
    ("referrer-policy", "Referrer-Policy", "Controla que datos viajan en el Referer"),
    ("permissions-policy", "Permissions-Policy", "Limita camara, microfono, etc."),
]
NOTAS = {6: "A", 5: "B", 4: "C", 3: "D", 2: "E"}


def main():
    print(f"{C}{B}=== AUDITOR DE CABECERAS HTTP ==={X}")
    print("Usalo solo en webs tuyas o con autorizacion.\n")
    url = input("URL a auditar (ej. https://tuweb.com): ").strip()
    if not url:
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    req = urllib.request.Request(url, headers={"User-Agent": "AuditorCabeceras/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ssl.create_default_context())
    except urllib.error.HTTPError as e:
        resp = e  # tambien tiene cabeceras
    except Exception as e:
        print(f"{R}No se pudo conectar: {e}{X}")
        return

    cabeceras = {k.lower(): v for k, v in resp.headers.items()}
    print(f"\n{B}Respuesta: {getattr(resp, 'status', getattr(resp, 'code', '?'))}  ->  {url}{X}\n")

    puntos = 0
    for clave, nombre, desc in CHECKS:
        if clave in cabeceras:
            puntos += 1
            print(f"  {G}[OK]  {nombre:<24}{X} {desc}")
        else:
            print(f"  {R}[FALTA] {nombre:<22}{X} {desc}")

    print(f"\n{B}Otros puntos:{X}")
    for h in ("server", "x-powered-by"):
        if h in cabeceras:
            print(f"  {Y}[!] {h}: {cabeceras[h]}{X}  (revela tecnologia; mejor ocultarlo)")
    cookies = resp.headers.get_all("Set-Cookie") or []
    for ck in cookies:
        bajo = ck.lower()
        fallos = [f for f in ("secure", "httponly", "samesite") if f not in bajo]
        nombre = ck.split("=")[0]
        if fallos:
            print(f"  {Y}[!] Cookie '{nombre}' sin: {', '.join(fallos)}{X}")
        else:
            print(f"  {G}[OK] Cookie '{nombre}' bien configurada{X}")
    if not url.startswith("https://"):
        print(f"  {R}[!] La URL usa HTTP sin cifrar{X}")

    nota = NOTAS.get(puntos, "F")
    color = G if puntos >= 5 else (Y if puntos >= 3 else R)
    print(f"\n{B}Nota final: {color}{nota}{X}{B}  ({puntos}/6 cabeceras){X}")


if __name__ == "__main__":
    main()
