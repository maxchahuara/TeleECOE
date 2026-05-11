import socket
import concurrent.futures

def check_ports(ip):
    res = []
    for port in [8000, 554, 80]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex((ip, port)) == 0:
                res.append((ip, port))
        except:
            pass
        finally:
            s.close()
    return res

ips = [f'172.18.4.{i}' for i in range(1, 255)]
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as e:
    found = [item for sublist in e.map(check_ports, ips) for item in sublist]
    
print("Found IPs/Ports:", found)
