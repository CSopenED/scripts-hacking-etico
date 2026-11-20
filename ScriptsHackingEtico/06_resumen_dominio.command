#!/bin/bash
cd "$(dirname "$0")/scripts" || exit 1
clear
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 no esta instalado. Ejecuta: xcode-select --install"
  read -n 1 -s -r -p "Pulsa una tecla para cerrar..."; exit 1
fi
python3 "dominio_dns.py"
echo
read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
