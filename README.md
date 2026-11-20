# 🛡️ Scripts de Hacking Ético

Colección de 13 scripts en Python para aprender ciberseguridad práctica: reconocimiento, defensa, forense/OSINT y laboratorio/CTF. Pensados para **macOS**, con lanzadores de doble clic, pero el código es Python puro y funciona en cualquier sistema.

> ⚠️ **Uso exclusivamente educativo.** Usa estas herramientas solo en tus propios equipos, redes y dominios, o con autorización expresa por escrito. Acceder a sistemas ajenos sin permiso es delito (Código Penal, arts. 197 y siguientes). Este repositorio no se responsabiliza del uso indebido del contenido.

📘 Incluye un **manual completo en PDF** (`ScriptsHackingEtico/Manual_Scripts_HackerGuide.pdf`) con una página por script: qué hace, cómo se usa, cómo interpretar la salida y una idea de vídeo para cada uno.

---

## 📂 Categorías

### 🔍 Reconocimiento
*(sobre tus propios activos)*

| Script | Descripción |
|---|---|
| `01_auditor_cabeceras` | Nota de la A a la F de las cabeceras de seguridad HTTP de una web |
| `02_escaner_puertos` | Escáner de puertos TCP multihilo con lectura de banners |
| `06_resumen_dominio` | DNS, SPF, DMARC y WHOIS de un dominio en una sola pantalla |
| `09_enumerador_subdominios` | Subdominios vía certificate transparency (crt.sh), sin escanear la red |

### 🛡️ Defensa y análisis

| Script | Descripción |
|---|---|
| `03_honeypot` | Puerto trampa que registra quién intenta conectar |
| `04_comprobar_password` | Entropía de una contraseña + filtraciones (Have I Been Pwned, k-anonimato) |
| `07_monitor_integridad` | Hashes SHA-256 de una carpeta; detecta cambios, altas y bajas |
| `10_analizador_logs` | Detecta fuerza bruta e IPs sospechosas en logs de SSH o Apache/Nginx |

### 🕵️ Forense y OSINT
*(sobre tus propios datos)*

| Script | Descripción |
|---|---|
| `05_metadatos` | Metadatos ocultos de un archivo: GPS, cámara, autor, fechas |
| `11_huella_digital` | Informe HTML de qué perfiles públicos existen con tu usuario |

### 🧪 Laboratorio y CTF

| Script | Descripción |
|---|---|
| `08_decodificador_ctf` | Base64, hex, binario, URL, ROT13, César e identificador de hashes |
| `12_cracker_hashes` | Identifica el tipo de hash y prueba un diccionario de palabras |
| `13_fuzzer_directorios` | Busca rutas y archivos sensibles (`.env`, `admin`, `backup.zip`...) en una web |

---

## 🚀 Instalación

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO/ScriptsHackingEtico
```

### macOS — primera vez
Los archivos `.command` vienen de internet, así que macOS los bloquea la primera vez:

```bash
xattr -dr com.apple.quarantine .
chmod +x *.command
```

A partir de ahí, doble clic normal sobre cualquier `.command`.

### Cualquier sistema (Linux, Windows con Python)

```bash
cd scripts
python3 cabeceras.py
```

**Requisitos:** Python 3. Internet para `01`, `04`, `06`, `09`, `11` y `13`. `exiftool` opcional para más detalle en `05`.

---

## 🧭 Flujo recomendado

1. **Reconocer** → `01`, `02`, `06`, `09` sobre tus propios activos
2. **Defender y analizar** → `03`, `04`, `07`, `10`
3. **Forense y OSINT** → `05`, `11`
4. **Laboratorio y CTF** → `08`, `12`, `13` — practica en [TryHackMe](https://tryhackme.com), [Hack The Box](https://hackthebox.com), [DVWA](https://github.com/digininja/DVWA) o [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)

## 📄 Licencia

MIT. Úsalo, modifícalo y compártelo, pero siempre dentro de la ley y con el consentimiento de quien corresponda.
