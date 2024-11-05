from fragmentizador import *

dat1 = Datagrama("ola",1,1,1,1,1,7,True,10)
dat2 = Datagrama("chau",1,1,1,1,1,0,False,10)

mensaje = reensamblar([dat1,dat2],10)
print(mensaje)