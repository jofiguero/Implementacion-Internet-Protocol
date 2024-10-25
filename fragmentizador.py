import sys
import socket

class Vecino:
    def __init__(self, ip, puerto, mtu):
        self.ip = ip
        self.puerto = puerto
        self.mtu = mtu

    def __str__(self):
        return f"{self.ip}|{self.puerto}|{self.mtu}"
    
class Datagrama:
    def __init__(self, mensaje, ip_orig, p_orig, ip_dest, p_dest, ID):
        self.mensaje = mensaje
        self.ip_orig = ip_orig
        self.p_origen = p_orig
        self.ip_dest = ip_dest
        self.p_dest = p_dest
        self.ID = ID

    def __str__(self):
        return f"{self.mensaje}|{self.ip_orig}|{self.p_origen}|{self.ip_dest}|{self.p_dest}|{self.ID}"

    
def parse_datagram(datagram):
    splitted = datagram.split("|")
    return Datagrama(splitted[0],splitted[1],int(splitted[2]),splitted[3],int(splitted[4]),splitted[5])
    
def parse_address(address):
    """Parse an address of the form ip:puerto or ip:puerto:mtu."""
    parts = address.split(":")
    if len(parts) == 2:
        ip, puerto = parts
    else:
        raise ValueError(f"Dirección no válida: {address}")
    return ip, int(puerto)

def parse_neighbor_address(address):
    parts = address.split(":")
    if len(parts) == 3:
        ip, puerto, mtu = parts
    else: 
        raise ValueError(f"Dirección no válida: {address}")
    return ip, int(puerto), int(mtu)

def main():
    #Procesamos los argumentos
    if len(sys.argv) < 3:
        print("Uso: python fragmentizador.py mi_ip:mi_puerto ip:puerto:mtu ip:puerto:mtu ...")
        sys.exit(1)

    mi_ip_puerto = sys.argv[1]
    mi_ip, mi_puerto = parse_address(mi_ip_puerto)
        
    vecinos = []
    for destination in sys.argv[2:]:
        try:
            ip, puerto, mtu = parse_neighbor_address(destination)
            vec = Vecino(ip,puerto,mtu)
            vecinos += [vec]
        except ValueError as e:
            print(e)
    print("CREANDO EL SCOKET")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', mi_puerto))

    print("NOS PONDREMOS A ESCUCHAR")
    
    data = sock.recv(1024).decode()

    datagrama = parse_datagram(data)

    print(datagrama.p_dest == mi_puerto)
    print(datagrama.p_dest)
    print(mi_puerto)
    if datagrama.ip_dest == mi_ip and datagrama.p_dest == mi_puerto:
        print(datagrama.mensaje)
    else:
        print("No es para mi")


if __name__ == "__main__":
    main()
1