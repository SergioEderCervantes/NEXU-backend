# Documentación de Sockets de Chat para el Equipo de Frontend

Este documento describe cómo interactuar con el backend a través de WebSockets para la funcionalidad de chat en tiempo real.

## Conexión Inicial y Autenticación

Para establecer una conexión de socket, el cliente debe conectarse al endpoint del servidor de Socket.IO.

**¡Muy Importante!** La conexión debe incluir un JSON `auth` con el token JWT del usuario para la autenticación. El backend utiliza este token para verificar la identidad del usuario en el evento `connect`. Si el token no es válido o está ausente, la conexión será rechazada.

**Ejemplo de conexión en el cliente (JavaScript):**
```javascript
import { io } from "socket.io-client";

const jwt = "tu_json_web_token"; // El JWT obtenido del endpoint de login/signup

const socket = io("http://localhost:5000", { // Reemplaza con la URL de tu servidor
  auth: {
    token: jwt
  }
});

socket.on('connect', () => {
  console.log('Conectado al servidor de sockets con ID:', socket.id);
});

socket.on('disconnect', () => {
  console.log('Desconectado del servidor de sockets.');
});

// Escucha el mensaje de bienvenida del servidor
socket.on('message', (data) => {
  console.log('Mensaje del servidor:', data); // Ej: "Connected to server successfully and joined personal room."
});
```

---

## Eventos que el Cliente Envía al Backend

Estos son los eventos que el frontend debe emitir para interactuar con el servidor.

### 1. `start_chat`

Este evento se usa para iniciar una conversación con otro usuario. Si no existe un chat previo entre los dos, el backend creará uno nuevo.

-   **Evento:** `start_chat`
-   **Payload (lo que se envía):** Un objeto JSON con los siguientes campos:
    -   `target_id` (string): El ID del usuario con el que se quiere iniciar el chat.
    -   `content` (string): El contenido del primer mensaje.
-   **Ejemplo:**
    ```javascript
    socket.emit('start_chat', {
      target_id: 'ID_del_otro_usuario',
      content: '¡Hola! ¿Cómo estás?'
    });
    ```

### 2. `dm` (Direct Message)

Este evento se utiliza para enviar un mensaje dentro de una conversación ya existente.

-   **Evento:** `dm`
-   **Payload (lo que se envía):** Un objeto JSON con:
    -   `target_id` (string): El ID del **chat** (o conversación) al que se envía el mensaje.
    -   `content` (string): El contenido del mensaje.
-   **Ejemplo:**
    ```javascript
    socket.emit('dm', {
      target_id: 'ID_de_la_conversacion',
      content: 'Nos vemos mañana.'
    });
    ```

---

## Eventos que el Cliente Recibe del Backend

Estos son los eventos que el servidor puede emitir hacia el cliente. El frontend debe tener listeners para manejarlos.

### 1. Mensaje de Bienvenida (sin nombre de evento)

Justo después de una conexión exitosa, el servidor envía un mensaje simple de confirmación.

-   **Evento:** `message`
-   **Payload (lo que se recibe):** Un string con un mensaje de bienvenida.
-   **Ejemplo de Payload:**
    ```
    "Connected to server successfully and joined personal room."
    ```

### 2. `new_notification`

Este evento se recibe cuando otro usuario te envía un mensaje (ya sea en un chat nuevo o existente). Sirve para mostrar notificaciones en tiempo real.

-   **Evento:** `new_notification`
-   **Payload (lo que se recibe):** Un objeto JSON con los detalles del mensaje y el remitente.
    -   `chat_id` (string): El ID de la conversación a la que pertenece el mensaje.
    -   `sender_id` (string): El ID del usuario que envió el mensaje.
    -   `sender_name` (string): El nombre del usuario que envió el mensaje.
    -   `message` (string): El contenido del mensaje recibido.
-   **Ejemplo de Payload:**
    ```json
    {
      "chat_id": "chat_abc123",
      "sender_id": "user_456",
      "sender_name": "Juan Perez",
      "message": "¡Hola! ¿Viste el partido?"
    }
    ```

### 3. `client_error`

Se emite cuando el cliente envía datos incorrectos o incompletos en un evento.

-   **Evento:** `client_error`
-   **Payload (lo que se recibe):** Un objeto con un mensaje de error.
-   **Ejemplo de Payload:**
    ```json
    {
      "msg": "Target user ID and first message are required"
    }
    ```

### 4. `server_error`

Se emite cuando ocurre un error inesperado en el servidor al procesar una solicitud del cliente (por ejemplo, un chat no encontrado).

-   **Evento:** `server_error`
-   **Payload (lo que se recibe):** Un objeto con un mensaje de error.
-   **Ejemplo de Payload:**
    ```json
    {
      "msg": "El chat no fue encontrado"
    }
    ```
