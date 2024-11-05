import sys
import socket
import time
import random

"""
Clase que representa a un Vecino de un router.

Atributos:
ip (str): la direccion ip del router vecino
puerto (int): el puerto del router vecino
mtu (int): el mtu del router vecino
"""
class Vecino:
    def __init__(self, ip, puerto, mtu):
        self.ip = ip
        self.puerto = puerto
        self.mtu = mtu

    def __str__(self):
        return f"{self.ip}|{self.puerto}|{self.mtu}"

"""
Clase que representa a un Datagrama

Atributos:
mensaje (str): Mensaje que transporta el datagrama
ip_orig (str): IP del router desde el que fue enviado el datagrama originalmente
p_orig (int): Puerto desde el cual fue enviado el datagrama originalmente
ip_dest (str): IP del router al que se dirige el datagrama
p_dest (int): Puerto al cual se dirige el datagrama
ID (str): identificador único del mensaje del que viene el datagrama
offset (int): Ubicación medida en caracteres desde el inicio del string en donde debería quedar el mensaje del datagrama
ultimo (bool): Bool que indica si este es el ultimo datagrama del mensaje o no
largo_total (int): Largo total del mensaje en caracteres
ttt (int): time to travel, mecanismo para detener loops (mayor explicación en el readme)
trapped (bool): Indica si un mensaje está probablemente atrapado en un loop o no
ttl (int): time to live, contador para determinar si un mensaje ya viajó demasiado y debe ser descartado
"""   
class Datagrama:
    def __init__(self, mensaje, ip_orig, p_orig, ip_dest, p_dest, ID, offset, ultimo,largo_total,ttt,trapped,ttl):
        self.mensaje = mensaje
        self.ip_orig = ip_orig
        self.p_orig = p_orig
        self.ip_dest = ip_dest
        self.p_dest = p_dest
        self.ID = ID
        self.offset = offset
        self.ultimo = ultimo
        self.largo_total = largo_total
        self.ttt = ttt
        self.trapped = trapped
        self.ttl = ttl

    def __str__(self):
        return f"{self.mensaje}|{self.ip_orig}|{self.p_orig}|{self.ip_dest}|{self.p_dest}|{self.ID}|{self.offset}|{self.ultimo}|{self.largo_total}|{self.ttt}|{self.trapped}|{self.ttl}"

"""
Funcion que recibe un datagrama y un entero llamado 'cantidad' y devuelve el datagrama fragmentado en 'cantidad' veces
"""
def fragmentar(datagrama, cantidad):
    largo = int(len(datagrama.mensaje)/cantidad+1)
    #Si el datagrama es demasiado pequeño para fragmentar, devolver solo el datagrama
    if largo > (len(datagrama.mensaje)):
        return [datagrama]
    fragmentos = []
    #Fragmentamos
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
                              datagrama.largo_total,
                              datagrama.ttt,
                              False,
                              datagrama.ttl)
        fragmentos += [particion]

        if offset + len(sub_mensaje) == len(datagrama.mensaje):
            break

    return fragmentos


"""
Recibe una lista de fragmentos y un largo total del mensaje y reensambla el mensaje entero
"""
def reensamblar(fragmentos,largo_total):
    mensaje = ""
    for i in range(largo_total):
        mensaje += "+"
    
    for fragmento in fragmentos:
        offset = fragmento.offset
        sub_mensaje = fragmento.mensaje
        mensaje = mensaje[:offset] + sub_mensaje + mensaje[offset+len(sub_mensaje):]
    return mensaje

"""
Recibe la representación en string de un datagrama y lo parsea devolviendo una instancia de la clase Datagrama
"""
def parse_datagram(datagram):
    splitted = datagram.split("|")
    if splitted[7] == "True":
        ultimo = True
    elif splitted[7] == "False":
        ultimo = False
    else:
        ultimo = None
    if splitted[10] == "True":
        trapped = True
    elif splitted[10] == "False":
        trapped = False
    else:
        trapped = None

    return Datagrama(splitted[0],splitted[1],int(splitted[2]),splitted[3],int(splitted[4]),splitted[5],int(splitted[6]),ultimo,int(splitted[8]),int(splitted[9]),trapped,int(splitted[11]))

"""
Recibe una direccion propia y la parsea
"""
def parse_address(address):
    """Parse an address of the form ip:puerto or ip:puerto:mtu."""
    parts = address.split(":")
    if len(parts) == 2:
        ip, puerto = parts
    else:
        raise ValueError(f"Dirección no válida: {address}")
    return ip, int(puerto)

"""Recibe la direccion de un vecino y la parsea"""
def parse_neighbor_address(address):
    parts = address.split(":")
    if len(parts) == 3:
        ip, puerto, mtu = parts
    else: 
        raise ValueError(f"Dirección no válida: {address}")
    return ip, int(puerto), int(mtu)
"""
Recibe una lista de fragmentos y los imprime
Cumple funciones de debuging
"""
def printear_fragmentos(fragmentos):
    for fragmento in fragmentos:
        print(fragmento)
        print(len(str(fragmento)))

"""
Recibe una lista de vecinos y un largo de mensaje, si es que hay algun vecino dentro de la lista que pueda recibir el mensaje entero,
lo retorna, de lo contrario, retorna False.
"""
def investigador(vecinos,largo):
    ret = False
    for vecino in vecinos:
        if vecino.mtu > largo:
            ret = vecino
            break
    return ret

"""
Recibe una lista de vecinos y devuelve el mtu minimo entre todos
"""
def mtu_minimo(vecinos):
    min = vecinos[0].mtu
    for vecino in vecinos:
        if vecino.mtu < min:
            min = vecino.mtu
    return min

"""
Programa que actua como Router
"""
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
    id_actual = None
    while True:
        try: 
            #Randomizamos el orden de los vecinos
            random.shuffle(vecinos)
            print("NOS PONDREMOS A ESCUCHAR")
            
            data = sock.recv(5000).decode()
            print("Me llegó algo")

            datagrama = parse_datagram(data)

            if datagrama.ip_dest == mi_ip and datagrama.p_dest == mi_puerto:
                print("Es para mi, los empezaré a unir")
                #Si es que este es el primer datagrama que nos llega de un mensaje, seteamos el id del mensaje que estamos recibiendo
                if id_actual == None:
                    id_actual = datagrama.ID
                #Si es que ya estamos recolectando los datagramas de un mensaje y recibimos un datagrama de otro mensaje, lo botamos.
                elif id_actual != datagrama.ID:
                    pass
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
                    id_actual = None
                    print(mensaje)
                    print("MENSAJE RECIBIDO CON EXITO!")

            else:
                print("No es para mi")
                #Si no es para mi y no tengo a quien enviarselo, o si es que time to live llegó a cero
                if len(vecinos) == 0 or datagrama.ttl == 0:
                    print("Botaré el paquete")
                    pass
                
                #Buscamos si hay algun vecino con mtu mayor o igual que el tamaño del datagrama pasado a string
                investigacion = investigador(vecinos,len(str(datagrama)))
                #Si el datagrama no está atrapado y hay alguien a quien le quepa el mensaje entero
                if not datagrama.trapped and investigacion != False:
                    print("Hay alguien con el mtu lo suficientemente grande ")
                    print(f"Voy a reenviar '{datagrama.mensaje}' a {investigacion.ip},{investigacion.puerto}")
                    #Enviar el mensaje por ahí
                    datagrama.ttl -= 1
                    datagrama.ttt -= 1
                    if datagrama.ttt == 0:
                        datagrama.trapped = True
                        datagrama.ttt = 20
                    
                    sock.sendto(str(datagrama).encode(),(investigacion.ip,investigacion.puerto))
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
                            datagrama.ttl -= 1
                            datagrama.ttt -= 1
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
            id_actual = None
            recibidos = []
            acumulador = 0
            print("MENSAJE RECIBIDO INCOMPLETO")

if __name__ == "__main__":
    main()
