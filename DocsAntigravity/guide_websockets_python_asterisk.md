# Guía Completa: Desarrollo de Aplicaciones con WebSockets, Python y Asterisk

Esta guía te explicará cómo crear un servidor o servicio para gestionar y enviar llamadas a través de WebSockets, apoyándonos en la información de tus libros de NotebookLM y el código real que tienes en tu *workspace*. 

Aprenderemos a desarrollar este tipo de aplicaciones entendiendo el "por qué" de cada línea y comando.

---

## 1. Conceptos Básicos y Configuraciones de Asterisk

Para que Asterisk pueda comunicarse mediante WebSockets, utiliza su interfaz **ARI** (*Asterisk REST Interface*). ARI permite a aplicaciones externas (como tu código Python o frontend en JavaScript) conectarse por un WebSocket para recibir eventos en tiempo real, y usar peticiones HTTP REST para enviar comandos a la llamada.

### Configuraciones Necesarias en Asterisk (`/etc/asterisk/`):

1. **`http.conf`**: Habilita el servidor web interno de Asterisk, el cual es la base para aceptar conexiones WebSocket.
   - `enabled = yes` (Habilita el servidor)
   - `bindaddr = 0.0.0.0` (Escucha en todas las interfaces)
   - `bindport = 8088` (Puerto estándar)
2. **`ari.conf`**: Habilita la API Rest y configura el usuario de acceso.
   - `enabled = yes`
   - Se crea un usuario (ej: `[astuser2]`) con una contraseña (`type = user`, `password = asterisk`, `read_only = no`).
3. **`extensions.conf` (Dialplan)**: Se le indica a Asterisk que entregue el control de la llamada a nuestra app externa.
   - `exten => 100,1,Stasis(survey)`: Cuando entra una llamada, se ejecuta la aplicación Stasis llamada `survey`. Nuestra app en Python estará escuchando eventos de `survey`.

---

## 2. El Servidor Backend en Python: Manejo de ARI por WebSockets

En tu archivo [compose/django/server/websocketari.py](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/server/websocketari.py), tenemos un script en Python que se conecta como cliente de WebSocket hacia Asterisk para controlar el flujo de una llamada (en este caso, una encuesta o *survey*).

### Explicación línea por línea del script [websocketari.py](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/server/websocketari.py):

```python
import websocket
from ari import ARI
import rel
import json
```
- **`import websocket`**: Importa la librería `websocket-client`, utilizada para conectarnos al WebSocket de Asterisk y escuchar eventos en tiempo real.
- **`from ari import ARI`**: Importa una librería (probablemente personalizada) de Python para enviar peticiones HTTP REST a Asterisk (como colgar, contestar, o reproducir audios).
- **`import rel`**: Librería para el manejo del *event loop* del websocket (Regular Event Loop), asegurando que el socket se mantenga abierto de forma asíncrona.
- **`import json`**: Permite decodificar los eventos que envía Asterisk, los cuales vienen en formato texto JSON.

#### Clase SurveyAri
```python
class SurveyAri:
    survey_options = [...] # Lista de opciones de encuestas con audios.
    def __init__(self, max_attempts=3):
        # Mantiene el estado de la llamada para cada canal conectada.
```
- Se utiliza el paradigma de programación orientada a objetos para guardar el estado de una llamada. Dado que el WebSocket recibe eventos de *muchas* llamadas mezcladas, necesitamos una clase que recuerde en qué pregunta va cada persona.

#### Manejo de Mensajes del WebSocket
```python
memory_route = {} # Un diccionario para guardar un objeto SurveyAri por cada ID de llamada (canal).

def on_message(ws, message):
    ari_object = ARI('astuser2', 'asterisk', host='asterisk')
    event_to_dict = json.loads(message)
    event = event_to_dict.get('type', 'default')
```
- **[on_message](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/server/websocketari.py#73-127)**: Esta es la función más importante (*callback*). Se dispara **cada vez** que Asterisk envía un mensaje a través del WebSocket.
- **`json.loads(message)`**: Convierte el texto JSON en un diccionario de Python.
- **`event = event_to_dict.get('type')`**: Extrae el tipo de evento (ej. si la llamada inició, si el usuario presionó una tecla, etc).

```python
    if event == 'StasisStart':
        channel = event_to_dict['channel']['id']
        if channel not in memory_route.keys():
            memory_route[channel] = SurveyAri()

        ari_object.answer(event_to_dict['channel']['id'])
        ari_object.playback(channel, memory_route[channel].get_sound())
```
- **`StasisStart`**: Asterisk nos avisa que una llamada acaba de entrar al Dialplan en la extensión [Stasis(survey)](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/ari_connect.js#72-140).
- **`channel.id`**: Identificador único de la llamada. Si la llamada es nueva, creamos un estado nuevo ([SurveyAri](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/server/websocketari.py#7-68)).
- **`ari_object.answer(...)` y [playback(...)](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/ari_connect.js#100-109)**: Enviamos peticiones REST a Asterisk para contestar la llamada y reproducir el audio de bienvenida.

```python
    if event == 'ChannelDtmfReceived':
        option = event_to_dict['digit']
        # Lógica para registrar qué tecla presionó el usuario...
```
- **`ChannelDtmfReceived`**: Evento de WebSocket que indica que la persona en el teléfono presionó una tecla. Aquí nuestro script detiene el audio actual y guarda la respuesta.

#### Conexión y Ejecución
```python
if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://asterisk:8088/ari/events?api_key=astuser2:asterisk&app=survey",
        ...
    )
    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.dispatch()
```
- **`websocket.WebSocketApp`**: Crea la conexión websocket dirigida al puerto configuado en `http.conf` (`8088`). Se le pasa la API Key (usuario:contraseña) y se suscribe específicamente a la aplicación `app=survey`.
- **`ws.run_forever`**: Mantiene el script vivo escuchando eventos permanentemente. `reconnect=5` hace que si el servidor de Asterisk se reinicia, el Python intente reconectar a los 5 segundos.

---

## 3. Servidor WebSocket hacia el Frontend (Django + Channels)

Mientras que el código anterior conectaba el backend Python hacia Asterisk, a veces necesitas que una interfaz web (frontend) sepa lo que pasa. Para ello, en Django se crean websockets usando **Django Channels**.

### Archivo: [ami_app/websocket.py](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/ami_app/websocket.py)
```python
from channels.generic.websocket import AsyncWebsocketConsumer
from ami_app.ami import AMIAsterisk

class WebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("ami_socket", self.channel_name)
        await self.send('{"msg": "connected"}')
```
- **`AsyncWebsocketConsumer`**: Es la clase base de Django Channels para manejar WebSockets asíncronos hacia clientes web (navegadores).
- **[connect()](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/ami_app/websocket.py#9-13)**: Se ejecuta cuando un navegador intenta conectarse al websocket. `self.accept()` permite la conexión. 
- **`group_add("ami_socket")`**: Suscribe este navegador al grupo "ami_socket". Así, si Asterisk genera un evento global, Django hace un *broadcast* (envía el mismo mensaje) a todos los navegadores conectados.

```python
    async def receive(self, text_data=None, bytes_data=None):
        if text_data == 'IAXPeers':
            AMIAsterisk().get_iax_peers()
```
- **[receive()](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/ami_app/websocket.py#14-17)**: Si el frontend web nos envía a nosotros (al backend) un mensaje por websockets (ej. el string `'IAXPeers'`), reaccionamos invocando un comando en Asterisk vía AMI.

---

## 4. Frontend en Javascript (Cliente de WebSocket)

Para que el usuario final controle o vea las llamadas, necesitas un frontend que se comunique con WebSockets. En tu workspace tienes dos ejemplos claros.

### Archivo: [static/js/websocket.js](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/websocket.js) (La clase Envoltorio)
```javascript
class WbSocket {
    constructor(uri, funAttr) {
        ...
    }
    getWs(){
        this.websocket = new WebSocket(this.uri);
        this.websocket.onmessage = this.funAttr;
        this.websocket.onclose = (error)=>{
            setTimeout(() => { this.getWs(); }, 1000); // RECONEXIÓN AUTOMÁTICA
        };
    }
}
```
- **`new WebSocket(this.uri)`**: Comando nativo del navegador para iniciar la conexión WebSocket.
- **`this.websocket.onmessage`**: Define qué función se llamará cuando lleguen mensajes desde el servidor.
- **El por qué de esta clase**: Los websockets nativos de JavaScript se desconectan si la red falla y no se vuelven a reconectar solos. Esta clase encapsula la reconexión ([onclose](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/websocket.js#13-19) hace un `setTimeout` para volver a conectarse al segundo). ¡Esencial en producción!

### Archivo: [static/js/ari_connect.js](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/ari_connect.js) (Comandos directos a Asterisk)
```javascript
const user = 'astuser2'
const passwd = 'asterisk'
const uri = `ws://localhost:8088/ari/events?api_key=${user}:${passwd}&app=apptest`
const ws = new WbSocket(uri, onEvents);
```
- ¡Ojo aquí! En este frontend te estás conectando **directamente** al ARI de Asterisk saltándote Python. Esto es útil para pruebas rápidas (app `apptest`).

```javascript
// Funciones asignadas a botones de la interfaz
const hold = document.getElementById('hold');
hold.addEventListener('click', ({target}) => {
    stasisObject.hold(); // Peticion de pausar llamada en espera
});

// onEvents -> Lo que llega desde Asterisk al frontend
function onEvents({data}){
    const event = JSON.parse(data);
    switch(event.type) {
        case 'StasisStart':
            // ¡Entró una llamada! Actualizamos el número en la pantalla (HTML)
            document.getElementById('display').innerHTML = event.channel.caller.number;
            stasisObject = new StasisApp(event.channel);
            stasisObject.answer() // Automáticamente le mandamos el comando de contestar
            break;
    }
};
```
- **Flujo**: Asterisk nos envía por WebSocket el aviso de `StasisStart`. Nuestro navegador extrae el número del que nos llaman (`channel.caller.number`), lo pinta en el HTML (`display`), y utiliza la clase [StasisApp](file:///home/charly/DevOps/Asterisk_Python/asterisk_agi/compose/django/static/js/ari_connect.js#72-140) para contestar.

```javascript
class StasisApp {
    // ... define el canal de la llamada actual ...
    async answer() {
        // Ejecuta un POST REST HTTP hacia Django o directo a Asterisk para contestar (`channels/{id}/answer`)
    }
}
```
- Es importante notar que Asterisk usa **WebSockets** únicamente para enviar los **eventos** de lo que ocurre en tiempo real, pero espera recibir **las acciones** (contestar, reproducir audio, colgar) mediante **peticiones HTTP (POST/DELETE)** regulares al API Rest, representadas aquí en las llamadas `fetch` de JavaScript o en la clase `ARI` de Python.

---

## 5. Resumen: ¿Por qué usamos esta arquitectura?

Desarrollar telefonía y comunicaciones en tiempo real moderna requería un salto cualitativo sobre los antiguos AGI (archivos estáticos de scripts). 
Usar WebSockets + ARI trae las siguientes ventajas de diseño:
1. **Asincronismo:** Al usar WebSockets en Python (`ws.run_forever()`) tu software es asíncrono; un único script de Python puede controlar cientos de llamadas vivas sin bloquearse.
2. **Re-utilización de tecnologías web:** Al conectar con Django Channels o JavaScript directamente en el Frontend, puedes pintar gráficamente lo que hace una PBX (Asterisk) y crear Paneles Web de Agentes de call center que respondan al instante.
3. **Escalabilidad**: Podrías sacar el código en Python a un servidor separado de donde instalaste Asterisk. Se comunicarían vía red a través de los websockets sin problemas de dependencias locales.
