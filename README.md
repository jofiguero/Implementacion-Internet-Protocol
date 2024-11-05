# Readme Tarea 2, Joaquin Figueroa Mora, 21.262.773-9

## Desiciones de diseño
- Para representar un datagrama (que en este caso será un mensaje con un header) se optó por construir una clase __Datagrama__ para lograr una modularizacion de los datos necesarios y un acceso mas directo y sencillo a sus atributos. Al ser una clase, no era posible enviarlo via socket.send() por lo que se usó la clasica función __str__ para construir una version atomizada y parseable de el mensaje, cuyos atributos eran separados por el caracter "|". Para enviar un mensaje, antes de codificarlo se transformaba a string, y al recibir un mensaje se usa la funcion parse_datagram() que toma el string y retorna una instancia de __Datagrama__ equivalente.

- Para simplificar la implementación se optó por manejar los tamaños de envio y recepcion en caracteres, de modo que cada datagrama tiene un tamaño representado por la suma de el tamaño del mensaje a enviar y el header, que haciendo calculos aproximados, ronda los 50 caracteres (esto varía a consideración de las diversas variables que tiene el header), **enviar un archivo de texto muy grande podría arrojar un error dado que la funcion recv esta configurada para recibir 5000 caracteres en el codigo, de necesitar enviar un archivo mas grande, por favor modifique la linea XXX del código colocando un número superior en al menos 100 caracteres al largo del mensaje que se desea enviar**.

- Para fragmentar un datagrama se extrae su mensaje y se observa cual de los vecinos es el que tiene el menor mtu, usando este como referencia para aproximar con un tanteo cuantos trozos de ese largo serán necesarios para abarcar todo el mensaje (incluyendo los headers de cada mensaje). Luego teniendo esa cantidad, se llama a la funcion fragmentar, que recibe el datagrama a fragmentar y la cantidad de trozos en la que se desea separar el mensaje y devuelve la lista con los mensajes ya fragmentados.

- Para reensamblar un mensaje una vez se tienen todos los datagramas que corresponden a este mensaje, se crea un string del tamaño del mensaje final (este se sabe pues es un dato del header) que tiene solo simbolos '+', posteriormente se va rellenando este string con los mensajes portados por los datagramas usando los offsets que vienen en cada uno.

- En la función recibir, luego de haber recibido efectivamente todos los mensajes esperados, se esperan 3 segundos extras por si se recibe nuevamente un mensaje por parte del emisor (lo que significaría que no recibió el ack) y se reenvian los ack necesarios. Esto provoca que un envio de mensajes se demora un minimo de 3 segundos aun si el mensaje es pequeño.


## Como ejecutar la tarea

Enn caso de que le sirva, me tomé la libertad de hacer un script que facilita la ejecución y el testing de la tarea para hacerlo mas dinamico y entendible. Para ocuparlos se debe realizar lo siguiente:

Primero, se deben descargar los archivos de la tarea, en particular los archivos __enviador.py__ y __fragmentizador.py__. Estos deben quedar en el mismo directorio.

Se crearon varias estructuras de red para testear la tarea, en particular dejaré a continuacion los comandos para ejecutar cada uno de los casos:

1) Caso de fragmentación inicial: En este caso, se cuenta con 5 routers distribuidos de la siguiente manera:

              8082
             /    \
        120 /      \500
           /        \       500
       8084          8081---------8080
           \        /
        200 \      /500
             \    /
              8083

Cada vertice es un router y el numero es el puerto del router, cada eje es un enlace bidireccional y el numero es el mtu de dicho enlace (con enlaces bidireccionales me refiero a que hay dos enlaces unidireccionales, uno en cada sentido, de esta manera se prueba un caso mucho mas complejo que es el de los loops)
En este caso, se le envía un mensaje desde una sexta terminal hacia el puerto 8084, donde el objetivo de este mensaje es llegar al puerto 8080. Si el mensaje enviado es de mayor tamaño que 200, el mensaje deberá fragmentarse obligatoriamente para pasar hacia 8082 o 8083, sin embargo desde ahí en adelante, no se tendrá problemas en seguir avanzando pues los fragmentos ya serán menores al mtu de los enlaces que conectan con 8081.

Para activar este caso, primero ejecute los siguientes comandos en diferentes terminales:

python3 fragmentizador.py 127.0.0.1:8084 127.0.0.1:8082:120 127.0.0.1:8083:200

python3 fragmentizador.py 127.0.0.1:8083 127.0.0.1:8084:200 127.0.0.1:8081:500

python3 fragmentizador.py 127.0.0.1:8082 127.0.0.1:8084:120 127.0.0.1:8081:500

python3 fragmentizador.py 127.0.0.1:8081 127.0.0.1:8082:500 127.0.0.1:8083:500 127.0.0.1:8080:500

python3 fragmentizador.py 127.0.0.1:8080 127.0.0.1:8081:500



2) Luego, se abren dos terminales y se navega hacia el directorio creado para almacenar los archivos usando el comando cd de la forma:
**´´cd ruta/hacia/directorio**

3) Posteriormente se debe ejecutar el programa Persona2.py en una de las dos terminales, que es quien hace de servidor, para posteriormente ejecutar el programa Persona1.py en la otra terminal, que es quien hace de cliente.

Esto se realiza con los siguientes comandos: 

- python Persona2.py
- python Persona1.py

4) La terminal cliente, consultará si es que se desea enviar un mensaje propio o generar uno predeterminado con un largo especifico, usted podrá escoger entre estas dos opciones (Luego de que el servidor haya avisado que la conexion fue establecida, si lo presiona muy rapido podría lanzar error):

- La primera alternativa es enviar un mensaje propio, que se deberá escribir o copiar en la consola cliente

- La segunda alternativa es enviar un mensaje generado cuyo largo es definido por usted, los largos probados (sin forzar perdida de paquetes) son de hasta 10.000 caracteres, no se ha explorado mas allá, podría tardar mucho.

Cabe aclarar que la ventana de envío escogida en la tarea es pequeña, razón por la cual un archivo muy grande podría tardar en enviarse, pero eventualmente debería llegar.

5) Si se desea aplicar una simulacion de perdida de paquetes para estudiar si la tarea cumple con ser segura para enviar mensajes, se pueden usar los siguientes comandos en la terminal: 

Para setear una perdida del x% de los paquetes:
sudo tc qdisc add dev lo root netem loss 20%

Para consultar la perdida actual:
tc qdisc show dev lo

Para finalizar la simulacion de perdida:
sudo tc qdisc del dev lo root netem

Este ultimo comando es importante para regresar el computador a la normalidad luego del testing.

Muchas gracias por su tiempo.