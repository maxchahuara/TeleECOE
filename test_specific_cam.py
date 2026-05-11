import socket
import urllib.request

ip = "172.18.4.54"
port = 8000

print(f"Probando conexion TCP a {ip}:{port}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
try:
    result = sock.connect_ex((ip, port))
    if result == 0:
        print("El puerto 8000 esta ABIERTO. La camara acepta conexiones ONVIF.")
    else:
        print("El puerto 8000 esta CERRADO. Posible configuracion ONVIF apagada en esta camara.")
    sock.close()
except Exception as e:
    print(f"Error: {e}")

