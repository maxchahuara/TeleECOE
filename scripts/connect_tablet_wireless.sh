#!/usr/bin/env bash
set -euo pipefail

PORTS=(5000 1984 8555)
TABLET_URL="http://127.0.0.1:5000/tablet/"

usage() {
  cat <<'USAGE'
Uso:
  scripts/connect_tablet_wireless.sh pair <IP:PUERTO_EMPAREJAR> <CODIGO>
  scripts/connect_tablet_wireless.sh connect <IP:PUERTO_ADB>
  scripts/connect_tablet_wireless.sh auto

En Android:
  Ajustes > Sistema > Opciones de desarrollador > Depuracion inalambrica
  - "Emparejar dispositivo con codigo" muestra IP:puerto y codigo.
  - La pantalla principal de Depuracion inalambrica muestra otro IP:puerto para conectar.

El script crea tuneles ADB reverse para abrir en la tablet:
  http://127.0.0.1:5000/tablet/
USAGE
}

require_adb() {
  if ! command -v adb >/dev/null 2>&1; then
    echo "ERROR: adb no esta instalado o no esta en PATH." >&2
    exit 1
  fi
}

reverse_and_open() {
  local device="$1"
  echo "Configurando tuneles para ${device}..."
  for port in "${PORTS[@]}"; do
    adb -s "${device}" reverse "tcp:${port}" "tcp:${port}"
  done
  adb -s "${device}" shell am start -a android.intent.action.VIEW -d "${TABLET_URL}" >/dev/null
}

connect_known_devices() {
  mapfile -t devices < <(adb devices | awk 'NR > 1 && $2 == "device" {print $1}')
  if [ "${#devices[@]}" -eq 0 ]; then
    echo "ERROR: no hay tablets ADB conectadas/autorizadas." >&2
    adb devices -l >&2
    exit 1
  fi

  for device in "${devices[@]}"; do
    reverse_and_open "${device}"
  done

  echo
  echo "Listo. En la tablet debe abrirse:"
  echo "  ${TABLET_URL}"
  echo
  adb reverse --list
}

main() {
  require_adb
  local action="${1:-auto}"

  case "${action}" in
    pair)
      if [ "$#" -ne 3 ]; then
        usage >&2
        exit 2
      fi
      printf '%s\n' "$3" | adb pair "$2"
      echo "Emparejado. Ahora ejecuta:"
      echo "  scripts/connect_tablet_wireless.sh connect <IP:PUERTO_ADB>"
      ;;
    connect)
      if [ "$#" -ne 2 ]; then
        usage >&2
        exit 2
      fi
      adb connect "$2"
      connect_known_devices
      ;;
    auto)
      connect_known_devices
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
