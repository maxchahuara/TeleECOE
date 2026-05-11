from app import create_app
import os
import socket

def get_local_ip():
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
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes', 'on')
    print("----------------------------------------------------------------")
    print(" SISTEMA DE EVALUACIÓN INICIADO")
    print(f" PC MAESTRA: Accede a http://localhost:{port}")
    print(f" TABLETS:    Accede a http://{local_ip}:{port}/tablet")
    print("----------------------------------------------------------------")
    # host='0.0.0.0' es CRUCIAL para permitir conexiones externas
    app.run(host=host, port=port, debug=debug)
