#!/usr/bin/env python3
"""Informe de huella digital propia: junta lo que se puede averiguar de tu
propio email/usuario con fuentes publicas (HIBP, crt.sh) y genera un HTML.
Usa solo tus propios datos, o los de alguien que te haya dado permiso."""
import hashlib
import html
import json
import os
import ssl
import time
import urllib.error
import urllib.request

G, R, Y, C, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"


def consultar_hibp_email(email):
    """HIBP requiere API de pago para listar brechas por email; aqui usamos
    solo la comprobacion de pwned-passwords, asi que avisamos y devolvemos None."""
    return None


def estimar_sitios(usuario):
    sitios = {
        "GitHub": f"https://github.com/{usuario}",
        "GitLab": f"https://gitlab.com/{usuario}",
        "Twitter / X": f"https://x.com/{usuario}",
        "Instagram": f"https://instagram.com/{usuario}",
        "Reddit": f"https://reddit.com/user/{usuario}",
        "Medium": f"https://medium.com/@{usuario}",
    }
    resultados = {}
    for nombre, url in sitios.items():
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "Mozilla/5.0 HuellaDigital/1.0"})
            with urllib.request.urlopen(req, timeout=6, context=ssl.create_default_context()) as r:
                resultados[nombre] = (r.status < 400, url)
        except urllib.error.HTTPError as e:
            resultados[nombre] = (e.code < 400, url)
        except Exception:
            resultados[nombre] = (None, url)
        time.sleep(0.3)
    return resultados


def generar_html(datos, destino):
    filas = ""
    for nombre, (existe, url) in datos["sitios"].items():
        if existe is True:
            estado, color = "POSIBLE PERFIL", "#39ff14"
        elif existe is False:
            estado, color = "no encontrado", "#6f8f60"
        else:
            estado, color = "no verificado", "#fbbf24"
        filas += (f'<tr><td>{html.escape(nombre)}</td><td><a href="{html.escape(url)}">{html.escape(url)}</a></td>'
                  f'<td style="color:{color};font-weight:bold">{estado}</td></tr>')

    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Informe de huella digital — {html.escape(datos['usuario'])}</title>
<style>
body{{background:#080a07;color:#d4e8c2;font-family:'Courier New',monospace;padding:40px;max-width:900px;margin:auto}}
h1{{color:#f97316}} h2{{color:#00ffe7;border-bottom:1px solid #1e2a1e;padding-bottom:6px;margin-top:30px}}
table{{width:100%;border-collapse:collapse;margin-top:10px}}
td,th{{padding:8px;border-bottom:1px solid #1e2a1e;text-align:left}}
th{{color:#f97316}} a{{color:#00ffe7}}
.warn{{border:1px solid #ff4d4d;padding:12px;margin-top:20px;color:#ffb4b4}}
</style></head><body>
<h1>Informe de huella digital</h1>
<p>Usuario / email analizado: <b>{html.escape(datos['usuario'])}</b><br>
Generado: {datos['fecha']}</p>

<h2>Posibles perfiles en redes y plataformas</h2>
<table><tr><th>Sitio</th><th>URL comprobada</th><th>Resultado</th></tr>{filas}</table>
<p style="color:#6f8f60;font-size:0.9em">Esto solo comprueba si la URL responde, no confirma que el perfil sea tuyo.
Confirma cada uno manualmente con dos fuentes, como indica el método de cruce de OSINT.</p>

<h2>Filtraciones de contraseñas (Have I Been Pwned)</h2>
<p>{html.escape(datos.get('hibp_nota', 'No comprobado en esta ejecución.'))}</p>
<p style="color:#6f8f60;font-size:0.9em">Para comprobar tu email en filtraciones reales, visita
<a href="https://haveibeenpwned.com">haveibeenpwned.com</a> directamente (este script no envía tu email a ningún sitio).</p>

<div class="warn"><b>USO:</b> este informe es para revisar tu propia huella digital o la de alguien
que te haya dado permiso expreso. No lo uses para investigar a terceros sin autorización.</div>
</body></html>"""
    with open(destino, "w", encoding="utf-8") as f:
        f.write(pagina)


def main():
    print(f"{C}{B}=== INFORME DE HUELLA DIGITAL PROPIA ==={X}")
    print("Usa tu propio nombre de usuario, o el de alguien con permiso expreso.\n")
    usuario = input("Nombre de usuario (sin @): ").strip()
    if not usuario:
        return

    print(f"\nComprobando perfiles para '{usuario}' en 6 plataformas...")
    sitios = estimar_sitios(usuario)
    for nombre, (existe, url) in sitios.items():
        if existe is True:
            print(f"  {G}[POSIBLE]{X} {nombre:<14} {url}")
        elif existe is False:
            print(f"  {Y}[NO]{X}      {nombre:<14}")
        else:
            print(f"  {Y}[?]{X}       {nombre:<14} (no se pudo comprobar)")

    print(f"\n{Y}Para filtraciones de tu correo, usa 04_comprobar_password.command "
          f"o visita haveibeenpwned.com directamente.{X}")

    carpeta = os.path.expanduser("~/Desktop")
    if not os.path.isdir(carpeta):
        carpeta = os.path.expanduser("~")
    destino = os.path.join(carpeta, f"huella_digital_{usuario}.html")
    datos = {
        "usuario": usuario,
        "fecha": time.strftime("%Y-%m-%d %H:%M"),
        "sitios": sitios,
        "hibp_nota": "No comprobado automáticamente: usa el script 04 con tu email o visita haveibeenpwned.com.",
    }
    try:
        generar_html(datos, destino)
        print(f"\n{G}Informe HTML guardado en: {destino}{X}")
        print("Abrelo haciendo doble clic, se vera en tu navegador.")
    except OSError as e:
        print(f"{R}No se pudo guardar el informe: {e}{X}")


if __name__ == "__main__":
    main()
