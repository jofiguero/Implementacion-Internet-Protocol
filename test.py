from fragmentizador import *

datagram = Datagrama("Quierounpanconquesoperoestamuycaroelquesonosequevoyahacerquizamehagounpanconjamon",'127.0.0.1',8081,'127.0.0.1',8080,1,0,True)

primera_fragmentacion = fragmentar(datagram,5)

for datagrama in primera_fragmentacion:
    print(datagrama)

print("")

segunda_fragmentacion = fragmentar(primera_fragmentacion[1],3)

for datagrama in segunda_fragmentacion:
    print(datagrama)

