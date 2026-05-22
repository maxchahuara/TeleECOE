#!/usr/bin/env bash
set -euo pipefail

PORTS=(5000 1984 8555)
TABLET_URL="http://127.0.0.1:5000/tablet/"

if ! command -v adb >/dev/null 2>&1; then
  echo "ERROR: adb no esta instalado o no esta en PATH." >&2
  exit 1
fi

mapfile -t DEVICES < <(adb devices | awk 'NR > 1 && $2 == "device" {print $1}')

if [ "${#DEVICES[@]}" -eq 0 ]; then
  echo "ERROR: no hay tablets autorizadas por ADB. Conecta la tablet por USB y acepta la depuracion." >&2
  adb devices -l >&2
  exit 1
fi

for DEVICE in "${DEVICES[@]}"; do
  echo "Configurando tunel USB para ${DEVICE}..."
  for PORT in "${PORTS[@]}"; do
    adb -s "${DEVICE}" reverse "tcp:${PORT}" "tcp:${PORT}"
  done
  adb -s "${DEVICE}" shell am start -a android.intent.action.VIEW -d "${TABLET_URL}" >/dev/null
done

echo
echo "Listo. En cada tablet conectada abre:"
echo "  ${TABLET_URL}"
echo
echo "Puertos reenviados:"
adb reverse --list
