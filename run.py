from app import create_app
import fcntl
import os
import socket
import struct

def get_interface_ip(interface_name):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            request_data = struct.pack('256s', interface_name[:15].encode('utf-8'))
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, request_data)[20:24])
    except OSError:
        return None

def get_local_ip():
    configured_host = os.environ.get('TABLET_HOST')
    if configured_host:
        return configured_host

    hotspot_ip = get_interface_ip('ap0')
    if hotspot_ip:
        return hotspot_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conectamos a una IP pública (Google DNS) para saber nuestra IP local
        # No envía datos reales, solo consulta al sistema operativo qué interfaz usaría
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

app = create_app()

if __name__ == '__main__':
    local_ip = get_local_ip()
    tablet_url = os.environ.get('TABLET_URL') or f"http://{local_ip}:{os.environ.get('FLASK_PORT', '5000')}/tablet/"
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes', 'on')
    print("----------------------------------------------------------------")
    print(" SISTEMA DE EVALUACIÓN INICIADO")
    print(f" PC MAESTRA: Accede a http://localhost:{port}")
    print(f" TABLETS:    Accede a {tablet_url}")
    print("----------------------------------------------------------------")
    # host='0.0.0.0' es CRUCIAL para permitir conexiones externas
    app.run(host=host, port=port, debug=debug)
