# Endpoints Documentation

This document outlines the usage of the user-related API endpoints.

---

## 1. Get All Users

**Endpoint:** `GET /users/`

**Description:** Retrieves a list of all registered users in the system.

**Authentication:** Required. This endpoint needs a valid JSON Web Token (JWT) provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of user objects.
    ```json
    {
        "data": [
            {
                "id": "293847",
                "name": "Eder",
                ...
            }
        ]
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al obtener usuarios."
    }
    ```

---

## 2. Get or Update Current User Profile

**Endpoint:** 
- `GET /users/me`
- `PUT /users/me`

**Description:** 
- **GET:** Retrieves the profile information of the currently authenticated user.
- **PUT:** Updates the profile information of the currently authenticated user.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

### GET Request
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** A single user object with populated tag names.
    ```json
    {
        "data": {
            "id": "293847",
            "name": "Eder",
            "email": "al0293847@example.com",
            "tags": ["Programación", "Diseño Gráfico"],
            ...
        }
    }
    ```
*   **Error (401 Unauthorized):**
    ```json
    {
        "error": "Token is missing or invalid!"
    }
    ```

### PUT Request
*   **Method:** `PUT`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`
    *   `Content-Type: application/json`
*   **Body (JSON):**
    A JSON object containing the fields to update. Only `name`, `career`, `date_of_birth`, and `tag_ids` are updatable.
    ```json
    {
        "name": "Eder Updated",
        "career": "Software Engineer",
        "date_of_birth": "2000-01-01",
        "tag_ids": ["29a09700-ba37-4a48-b870-273fbe417867"]
    }
    ```

**Response:**
*   **Success (200 OK):**
    *   **Body:** The updated user object with populated tag names.
    ```json
    {
        "data": {
            "id": "293847",
            "name": "Eder Updated",
            "email": "al0293847@example.com",
            "career": "Software Engineer",
            "tags": ["Programación"],
            ...
        }
    }
    ```
*   **Error (400 Bad Request):** If the request body is missing or not a valid JSON.
*   **Error (404 Not Found):** If the user is not found.
*   **Error (500 Internal Server Error):** For unexpected issues.

---

## 3. Get User by ID

**Endpoint:** `GET /users/<user_id>`

**Description:** Get details of a specific user by their ID.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** The user object (password excluded).
    ```json
    {
        "data": {
            "id": "some-user-id",
            "name": "Another User",
            "email": "another@example.com",
            ...
        }
    }
    ```
*   **Error (404 Not Found):** If the user is not found.
*   **Error (500 Internal Server Error):** For unexpected issues.

---

## 4. User Signup

**Endpoint:** `POST /users/signup`

**Description:** Registers a new user account.

**Authentication:** None required.

**Request:**
*   **Method:** `POST`
*   **Headers:**
    *   `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "name": "New User",
        "email": "new@example.com",
        "password": "a_secure_password",
        "gender": "Masculino"
    }
    ```

**Response:**
*   **Success (201 Created):**
    ```json
    {
        "data": {
            "access_token": "your_newly_generated_jwt",
            "token_type": "bearer"
        }
    }
    ```
*   **Error (409 Conflict):** If a user with the same email already exists.

---

## 5. User Login

**Endpoint:** `POST /users/login`

**Description:** Authenticates an existing user and returns a JWT.

**Authentication:** None required.

**Request:**
*   **Method:** `POST`
*   **Headers:**
    *   `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "email": "existinguser@example.com",
        "password": "theirpassword123"
    }
    ```

**Response:**
*   **Success (200 OK):**
    ```json
    {
        "data": {
            "access_token": "your_generated_jwt",
            "token_type": "bearer"
        }
    }
    ```
*   **Error (401 Unauthorized):** If credentials are incorrect.

---

## 6. Upload User Avatar

**Endpoint:** `POST /users/upload_avatar`

**Description:** Uploads or updates the profile picture for the currently authenticated user. The image is sent as a `multipart/form-data` request.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

**Request:**
*   **Method:** `POST`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`
    *   `Content-Type: multipart/form-data`
*   **Body (Form Data):**
    *   **Key:** `avatar`
    *   **Value:** The image file (e.g., `my_picture.jpg`).

**Example cURL Request:**
```bash
curl -X POST \
  http://your-domain.com/users/upload_avatar \
  -H "Authorization: Bearer <your_access_token>" \
  -F "avatar=@/path/to/your/image.jpg"
```

**Response:**
*   **Success (200 OK):**
    *   **Body:** Returns the updated user object, including the new `avatar_url`.
    ```json
    {
        "data": {
            "id": "293847",
            "name": "Eder",
            "email": "al0293847@example.com",
            "avatar_url": "https://res.cloudinary.com/",
            ...
        }
    }
    ```
*   **Error (400 Bad Request):** If the `avatar` file part is missing or the file has no name.
*   **Error (500 Internal Server Error):** For unexpected issues during the upload process.

---

## 7. Get All Tags

**Endpoint:** `GET /tags/`

**Description:** Retrieves a list of all available tags in the system.

**Authentication:** Required. This endpoint needs a valid JSON Web Token (JWT) provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of tag objects.
    ```json
    {
        "data": [
            {
                "id": "29a09700-ba37-4a48-b870-273fbe417867",
                "name": "Programación",
                "icon": "Code",
                "description": "Lenguajes de programación, desarrollo de software, algoritmos y estructuras de datos."
            },
            ...
        ]
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al obtener los tags."
    }
    ```

---

## 8. Get User Chats

**Endpoint:** `GET /chats/`

**Description:** Retrieves all chats for the currently authenticated user. For each chat, it includes details of the other participant and a count of unread messages.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of chat objects.
    ```json
    {
        "data": [
            {
                "id": "chat-id-1",
                "last_message_at": "2025-12-05T10:00:00Z",
                "other_user": {
                    "id": "user-id-2",
                    "name": "Other User",
                    "is_active": true,
                    "avatar_url": "https://example.com/avatar.png"
                },
                "unread_messages": 2,
                "last_message": {
                    "content": "Hello there!",
                    "timestamp": "2025-12-05T10:00:00Z"
                }
            },
            ...
        ]
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al obtener los chats."
    }
    ```

---

## 9. Get All Chats (Admin)

**Endpoint:** `GET /chats/all`

**Description:** Retrieves a list of all chats in the system. (Primarily for admin/debugging purposes).

**Authentication:** None.

**Request:**
*   **Method:** `GET`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of all chat objects.
    ```json
    {
        "data": [
            {
                "id": "chat-id-1",
                "user_a": "user-a-id",
                "user_b": "user-b-id",
                "last_message_at": "2025-12-05T10:00:00Z"
            },
            ...
        ]
    }
    ```

---

## 10. Get Chat Messages

**Endpoint:** `GET /chats/<chat_id>`

**Description:** Retrieves all messages for a specific chat, sorted by timestamp. The user must be a participant in the chat to access its messages.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of message objects.
    ```json
    {
        "data": [
            {
                "id": "message-id-1",
                "conversation_id": "chat-id-1",
                "sender_id": "user-id-1",
                "content": "Hello!",
                "timestamp": "2025-12-05T09:59:00Z",
                "delivered": true
            },
            ...
        ]
    }
    ```
*   **Error (403 Forbidden):** If the user is not a participant of the chat.
*   **Error (404 Not Found):** If the chat is not found.
*   **Error (500 Internal Server Error):** For unexpected issues.

---

## 11. Health Check

**Endpoint:** `GET /health/`

**Description:** A simple endpoint to check if the API is running.

**Authentication:** None.

**Request:**
*   **Method:** `GET`

**Response:**
*   **Success (200 OK):**
    *   **Body:** A simple text message.
    ```
    Api Funcionando en Flask!!
    ```

---

## 12. Get All Posts

**Endpoint:** `GET /posts/`

**Description:** Retrieves all posts for the feed, enriched with user and tag information.

**Authentication:** Required. A valid JSON Web Token (JWT) must be provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** An array of enriched post objects.
    ```json
    {
        "data": [
            {
                "id": "post-1",
                "description": "¡Hola a todos! Estoy buscando a alguien para pasear a mi perro los fines de semana. ¿A alguien le interesa?",
                "timestamp": "2025-12-05T10:00:00Z",
                "user": {
                    "id": "98c1c991-2f73-49c7-916d-2418dbe4192d",
                    "name": "Jostino",
                    "career": "ISC",
                    "avatar_url": "https://res.cloudinary.com/..."
                },
                "tag": {
                    "id": "29a09700-ba37-4a48-b870-273fbe417867",
                    "name": "Amante de los animales",
                    "icon": "PawPrint"
                }
            },
            ...
        ]
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al obtener las publicaciones."
    }
    ```

---

## 13. Create Post

**Endpoint:** `POST /posts/`

**Description:** Creates a new post.

**Authentication:** Required. A valid JSON Web Token (JWT) must be provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `POST`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`
    *   `Content-Type: application/json`
*   **Body (JSON):**
    ```json
    {
        "tag_id": "29a09700-ba37-4a48-b870-273fbe417867",
        "description": "¡Este es un nuevo post de prueba!"
    }
    ```

**Response:**
*   **Success (201 Created):**
    *   **Body:** The newly created post object (un-enriched).
    ```json
    {
        "data": {
            "id": "new-post-id",
            "user_id": "authenticated-user-id",
            "tag_id": "29a09700-ba37-4a48-b870-273fbe417867",
            "description": "¡Este es un nuevo post de prueba!",
            "timestamp": "2025-12-05T15:30:00.123456Z"
        }
    }
    ```
*   **Error (400 Bad Request):** If `tag_id` or `description` are missing from the request body.
*   **Error (500 Internal Server Error):** For unexpected issues during post creation.

---

## 14. Delete Post

**Endpoint:** `DELETE /posts/<post_id>`

**Description:** Deletes a post by its ID. Only the owner of the post can delete it.

**Authentication:** Required. A valid JSON Web Token (JWT) must be provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `DELETE`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    ```json
    {
        "message": "Publicación eliminada exitosamente."
    }
    ```
*   **Error (403 Forbidden):** If the user is not authorized to delete the post.
*   **Error (404 Not Found):** If the post is not found.
*   **Error (500 Internal Server Error):** For unexpected issues during post deletion.