# Readme Tarea 2, Joaquin Figueroa Mora, 21.262.773-9

## Desiciones de diseño
- Para representar un datagrama (que en este caso será un mensaje con un header) se optó por construir una clase __Datagrama__ para lograr una modularizacion de los datos necesarios y un acceso mas directo y sencillo a sus atributos. Al ser una clase, no era posible enviarlo via socket.send() por lo que se usó la clasica función __str__ para construir una version atomizada y parseable de el mensaje, cuyos atributos eran separados por el caracter "|". Para enviar un mensaje, antes de codificarlo se transformaba a string, y al recibir un mensaje se usa la funcion parse_datagram() que toma el string y retorna una instancia de __Datagrama__ equivalente.

- Para simplificar la implementación se optó por manejar los tamaños de envio y recepcion en caracteres, de modo que cada datagrama tiene un tamaño representado por la suma de el tamaño del mensaje a enviar y el header, que haciendo calculos aproximados, ronda los 50 caracteres (esto varía a consideración de las diversas variables que tiene el header), **enviar un archivo de texto muy grande podría arrojar un error dado que la funcion recv esta configurada para recibir 5000 caracteres en el codigo, de necesitar enviar un archivo mas grande, por favor modifique la linea 216 del código colocando un número superior en al menos 100 caracteres al largo del mensaje que se desea enviar**.

- Para fragmentar un datagrama se extrae su mensaje y se observa cual de los vecinos es el que tiene el menor mtu, usando este como referencia para aproximar con un tanteo cuantos trozos de ese largo serán necesarios para abarcar todo el mensaje (incluyendo los headers de cada mensaje). Luego teniendo esa cantidad, se llama a la funcion fragmentar, que recibe el datagrama a fragmentar y la cantidad de trozos en la que se desea separar el mensaje y devuelve la lista con los mensajes ya fragmentados.

- Para reensamblar un mensaje una vez se tienen todos los datagramas que corresponden a este mensaje, se crea un string del tamaño del mensaje final (este se sabe pues es un dato del header) que tiene solo simbolos '+', posteriormente se va rellenando este string con los mensajes portados por los datagramas usando los offsets que vienen en cada uno.

- En la función recibir, luego de haber recibido efectivamente todos los mensajes esperados, se esperan 3 segundos extras por si se recibe nuevamente un mensaje por parte del emisor (lo que significaría que no recibió el ack) y se reenvian los ack necesarios. Esto provoca que un envio de mensajes se demora un minimo de 3 segundos aun si el mensaje es pequeño.

- Para lograr mayor posibilidades de que los datagramas lleguen a su destino, cada vez que se recibe un mensaje se realiza un shuffle de la lista de vecinos para no siempre mirar al mismo enlace por primera vez.

- Cuando se están recibiendo datagramas de un mensaje específico, se activa un timeout por parte de quien los está recibiendo de forma que si dejan de llegar en un segundo y aún no se ha completado el mensaje, se imprime el mensaje a medio terminar y se avisa al usuario de que no se puedo reensamblar el mensaje.

- En caso de que se produzca un loop, existe un mecanismo para detectarlo e intentar terminarlo, forzando la fragmentación de los mensajes aún cuando hay enlaces en los que caben completos. Para esto se usa un atributo del datagrama llamado "ttt" o "time to travel", que para que funcione, debe ser siempre mas pequeño que el "ttl" o "time to live", ya que de esa forma el "ttl" solo bota los mensajes en casos en los que ya no hay remedio para acabar con los loops.

- En caso de recibir un datagrama que tenga un id distinto al mensaje cuyos datagramas se están almacenando en buffer, este será descartado.

- Tambien se incluye un atributo "ultimo" representado por un booleano que indica si el mensaje de este datagrama va al final al armar el mensaje completo. Este atributo se mantiene al fragmentar activandolo en el ultimo fragmento correspondiente solamente si es que el datagrama fragmentado ya tenia activo el atributo ultimo.


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

Luego active al enviador con el siguiente comando:

python3 enviador.py

Y siga las instrucciones de la terminal:
Si es que desea enviar un mensaje propio, responda uno, presione enter y luego escriba su mensaje.
Si desea un mensaje de un largo determinado, responda dos, presione entrer y luego ingrese el tamaño que desea que tome el mensaje.


2) Caso de fragmentación posterior: aca tambien se cuenta con 5 routers distribuidos de la siguiente forma:

              8082
             /    \
        500 /      \100
           /        \       500
       8084          8081---------8080
           \        /
        500 \      /100
             \    /
              8083

En este caso es directo apreciar que el problema se presentará al enviar los datagramas desde 8084 hacia 8082 o 8083, debido a que desde ahí, siempre eligirán devolverse a 8084, pues el mensaje cabe por ahí y eso es lo primero que se revisa, por lo que quedarían en un loop eterno. Es aquí donde cobra importancia el inventado 'ttt', al que llamo "time to travel". Este contador, al igual que su contraparte ttl (que tambien está presente) intenta ayudar a enfrentar los loops en casos como estos, salvando a los datagramas de quedarse "atrapados". Para esto hay otro atributo mas al que se llamó "trapped" que es un booleano, el cual es activado unicamente en caso de que el ttt llegue a cero. De estar activo, el proximo router que reciba el mensaje lo fragmentará directamente, sin preocuparse primero de si cabe por algun enlace.

Para activar este caso, primero ejecute los siguientes comandos en diferentes terminales:

python3 fragmentizador.py 127.0.0.1:8084 127.0.0.1:8082:500 127.0.0.1:8083:500

python3 fragmentizador.py 127.0.0.1:8083 127.0.0.1:8084:500 127.0.0.1:8081:100

python3 fragmentizador.py 127.0.0.1:8082 127.0.0.1:8084:500 127.0.0.1:8081:100

python3 fragmentizador.py 127.0.0.1:8081 127.0.0.1:8082:100 127.0.0.1:8083:100 127.0.0.1:8080:500

python3 fragmentizador.py 127.0.0.1:8080 127.0.0.1:8081:500

Luego active al enviador con el siguiente comando:

python3 enviador.py

Y siga las instrucciones de la terminal:
Si es que desea enviar un mensaje propio, responda uno, presione enter y luego escriba su mensaje.
Si desea un mensaje de un largo determinado, responda dos, presione entrer y luego ingrese el tamaño que desea que tome el mensaje.


Si se desea aplicar una simulacion de perdida de paquetes para estudiar si la tarea cumple con ser segura para enviar mensajes, se pueden usar los siguientes comandos en la terminal: 

Para setear una perdida del x% de los paquetes:
sudo tc qdisc add dev lo root netem loss 20%

Para consultar la perdida actual:
tc qdisc show dev lo

Para finalizar la simulacion de perdida:
sudo tc qdisc del dev lo root netem

Este ultimo comando es importante para regresar el computador a la normalidad luego del testing.

Muchas gracias por su tiempo.