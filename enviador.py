import socket
from fragmentizador import Datagrama

def formar_input():
    mensaje = input("Introduzca el mensaje" )
    return mensaje

def generar_mensaje_enorme(min_size):
    mensaje = ""
    while len(mensaje) < min_size:
        mensaje += "aaaaa"
        mensaje += "bbbbb"
        mensaje += "ccccc"
        mensaje += "ddddd"
        mensaje += "eeeee"
        mensaje += "fffff"
    return mensaje


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1',8081))
while True:
    
    desicion = input("¿Quieres enviar un mensaje propio (1) o un mensaje muy largo autogenerado (2)? ")

    if desicion == "1":
        mensaje = str(Datagrama(input("Ingresa tu mensaje: "),'127.0.0.1',8081,'127.0.0.1',8082,1))
        break

    elif desicion == "2":
        mensaje = str(Datagrama(generar_mensaje_enorme(int(input("Ingresa el largo que quieres que tenga el mensaje: "))),'127.0.0.1',8081,'127.0.0.1',8082,1))
        break

    else: 
        print("Input no valido")


sock.sendto(mensaje.encode(),('127.0.0.1',8080))
