import sys
import socket
import time
import random

class Vecino:
    def __init__(self, ip, puerto, mtu):
        self.ip = ip
        self.puerto = puerto
        self.mtu = mtu

    def __str__(self):
        return f"{self.ip}|{self.puerto}|{self.mtu}"
    
class Datagrama:
    def __init__(self, mensaje, ip_orig, p_orig, ip_dest, p_dest, ID, offset, ultimo,largo_total):
        self.mensaje = mensaje
        self.ip_orig = ip_orig
        self.p_orig = p_orig
        self.ip_dest = ip_dest
        self.p_dest = p_dest
        self.ID = ID
        self.offset = offset
        self.ultimo = ultimo
        self.largo_total = largo_total

    def __str__(self):
        return f"{self.mensaje}|{self.ip_orig}|{self.p_orig}|{self.ip_dest}|{self.p_dest}|{self.ID}|{self.offset}|{self.ultimo}|{self.largo_total}"

def fragmentar(datagrama, cantidad):
    largo = int(len(datagrama.mensaje)/cantidad+1)
    print(f"El largo del mensaje entero es {len(datagrama.mensaje)}")
    print(f"El largo de cada submensaje es {largo}")
    fragmentos = []
    for i in range(1,cantidad+1):
        
        sub_mensaje = datagrama.mensaje[largo*(i-1):min(largo*i,len(datagrama.mensaje))]
        
        offset = largo*(i-1) + datagrama.offset
        if i == cantidad or offset + len(sub_mensaje) == len(datagrama.mensaje):
            if datagrama.ultimo == True:
                ultimo = True
        else: 
            ultimo = False
        particion = Datagrama(sub_mensaje,
                              datagrama.ip_orig,
                              datagrama.p_orig,
                              datagrama.ip_dest,
                              datagrama.p_dest,
                              datagrama.ID,
                              offset,
                              ultimo,
                              datagrama.largo_total)
        fragmentos += [particion]

        if offset + len(sub_mensaje) == len(datagrama.mensaje):
            break

    return fragmentos

def reensamblar(fragmentos,largo_total):
    mensaje = ""
    for i in range(largo_total):
        mensaje += "+"
    
    for fragmento in fragmentos:
        offset = fragmento.offset
        sub_mensaje = fragmento.mensaje
        mensaje = mensaje[:offset] + sub_mensaje + mensaje[offset+len(sub_mensaje):]
    return mensaje
    
def parse_datagram(datagram):
    splitted = datagram.split("|")
    if splitted[7] == "True":
        ultimo = True
    elif splitted[7] == "False":
        ultimo = False
    else:
        ultimo = None

    return Datagrama(splitted[0],splitted[1],int(splitted[2]),splitted[3],int(splitted[4]),splitted[5],int(splitted[6]),ultimo,int(splitted[8]))
    
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

def printear_fragmentos(fragmentos):
    for fragmento in fragmentos:
        print(fragmento)
        print(len(str(fragmento)))

def investigador(vecinos,largo):
    ret = False
    for vecino in vecinos:
        if vecino.mtu > largo:
            ret = vecino
            break
    return ret

def mtu_minimo(vecinos):
    min = vecinos[0].mtu
    for vecino in vecinos:
        if vecino.mtu < min:
            min = vecino.mtu
    return min


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

    acumulador = 0
    recibidos = []
    while True:
        try: 
            #Randomizamos el orden de los vecinos
            random.shuffle(vecinos)
            print("NOS PONDREMOS A ESCUCHAR")
            
            data = sock.recv(10000).decode()
            print("Me llegó algo")

            datagrama = parse_datagram(data)
            #Almacenar en un diccionario todos los mensajes que voy recibiendo, en donde la llave sea el id de los mensajes y el contenido sea
            #una lista con todos los datagramas


            if datagrama.ip_dest == mi_ip and datagrama.p_dest == mi_puerto:
                print("Es para mi, los empezaré a unir")
                sock.settimeout(1)
                #Recibir y reensamblar los mensajes
                largo_total = datagrama.largo_total
                recibidos += [datagrama]
                acumulador += len(datagrama.mensaje)
                print("Fragmentos recibidos:")
                printear_fragmentos(recibidos)
                print(f"El acumulador es {acumulador}")
                if largo_total == acumulador:
                    mensaje = reensamblar(recibidos,largo_total)
                    sock.settimeout(None)
                    recibidos = []
                    acumulador = 0
                    print(mensaje)

            else:

                print("No es para mi")
                
                #Buscamos si hay algun vecino con mtu mayor o igual que el tamaño del datagrama pasado a string
                investigacion = investigador(vecinos,len(str(datagrama)))
                #Si lo hay 
                if investigacion != False:
                    print("Hay alguien con el mtu lo suficientemente grande ")
                    print(f"Voy a reenviar '{datagrama.mensaje}' a {investigacion.ip},{investigacion.puerto}")
                    #Enviar el mensaje por ahí
                    sock.sendto(str(datagrama).encode(),(investigacion.ip,investigacion.puerto))
                    print("Lo acabo de reenviar")
                #Si no lo hay
                else:
                    print("No hay nadie con mtu suficiente, habrá que fragmentar")
                    #Encontrar el mtu mas pequeño que tenga aluno de mis vecinos y usarlo para calcular el tanteo de cantidad
                    mtu = mtu_minimo(vecinos)
                    tanteo_cantidad = int(len(datagrama.mensaje)/(mtu-50)) + 1
                    print(f"Me tinca que deben ser {tanteo_cantidad} partes")
                    fragmentos = fragmentar(datagrama,tanteo_cantidad)

                    #Fragmentar el mensaje y dividir el envio entre los vecinos
                    por_enviar = len(fragmentos)
                    ind = 0
                    while por_enviar != 0:
                        for vecino in vecinos:
                            if por_enviar == 0:
                                break
                            sock.sendto(str(fragmentos[ind]).encode(),(vecino.ip,vecino.puerto))
                            print(f"reenvie '{fragmentos[ind].mensaje}' a {vecino.puerto}")
                            ind += 1
                            por_enviar -= 1
                            

                    print("reenvie todo")
        except socket.timeout:
            print("Algún mensaje se perdió en el camino, si rearmamos el mensaje se ve así:")
            mensaje = reensamblar(recibidos,largo_total)
            print(mensaje)
            sock.settimeout(None)
            recibidos = []
            acumulador = 0

            


if __name__ == "__main__":
    main()
