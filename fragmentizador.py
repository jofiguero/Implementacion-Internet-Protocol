import sys

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
    # Verifica que al menos se ha pasado mi_ip:mi_puerto y una ip:puerto:mtu
    if len(sys.argv) < 3:
        print("Uso: python fragmentizador.py mi_ip:mi_puerto ip:puerto:mtu ip:puerto:mtu ...")
        sys.exit(1)
    
    # Procesa mi_ip:mi_puerto
    mi_ip_puerto = sys.argv[1]
    mi_ip, mi_puerto = parse_address(mi_ip_puerto)
    
    print(f"Procesando desde IP: {mi_ip} en el puerto: {mi_puerto}")
    
    # Procesa las direcciones ip:puerto:mtu
    for destination in sys.argv[2:]:
        try:
            ip, puerto, mtu = parse_neighbor_address(destination)
            print(f"Destino: {ip}:{puerto} con MTU: {mtu}")
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
