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
    [
        {
            "id": 293847,
            "name": "Eder",
            "email": "al0293847@example.com",
            "is_active": true,
            "gender": "Masculino",
            "bio": "Software developer.",
            "reputation": 0
        },
        {
            "id": 293848,
            "name": "Another User",
            "email": "al0293848@example.com",
            "is_active": true,
            "gender": "Femenino",
            "bio": null,
            "reputation": 5
        }
    ]
    ```
    *Each user object will exclude the `password` field.*
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al obtener usuarios."
    }
    ```

---

## 2. Get Current User Profile

**Endpoint:** `GET /users/me`

**Description:** Retrieves the profile information of the currently authenticated user.

**Authentication:** Required. This endpoint needs a valid JSON Web Token (JWT) provided in the `Authorization` header as a Bearer token.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** A single user object.
    ```json
    {
        "id": 293847,
        "name": "Eder",
        "email": "al0293847@example.com",
        "is_active": true,
        "gender": "Masculino",
        "bio": "Software developer.",
        "reputation": 0
    }
    ```
    *The user object will exclude the `password` field.*
*   **Error (401 Unauthorized):**
    ```json
    {
        "error": "Token is missing or invalid!"
    }
    ```

---

## 3. User Signup

**Endpoint:** `POST /users/signup`

**Description:** Registers a new user account.

**Authentication:** None required.

**Request:**
*   **Method:** `POST`
*   **Headers:**
    *   `Content-Type: application/json`
*   **Body (JSON):** The following fields are required.
    ```json
    {
        "name": "New User",
        "email": "al0123456@example.com",
        "password": "a_secure_password",
        "gender": "Masculino",
        "bio": "Optional user biography."
    }
    ```
    *   `name` (string, required)
    *   `email` (string, required): Must be a valid email. The numeric prefix of the email (without `al`) will be used as the user `id`.
    *   `password` (string, required)
    *   `gender` (string, required)
    *   `bio` (string, optional)

**Response:**
*   **Success (201 Created):**
    ```json
    {
        "access_token": "your_newly_generated_jwt",
        "token_type": "bearer"
    }
    ```
*   **Error (400 Bad Request):** For missing JSON data or missing required fields (e.g., email).
    ```json
    {
        "error": "Se requiere un cuerpo de solicitud JSON."
    }
    ```
*   **Error (422 Unprocessable Entity):** For data validation errors (e.g., invalid email).
    ```json
    {
        "error": "Datos de entrada inválidos.",
        "detalles": [
            "El campo 'email' debe ser una dirección de email válida"
        ]
    }
    ```
*   **Error (409 Conflict):** If a user with the same email already exists.
    ```json
    {
        "error": "Ya existe un usuario con este email."
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al registrar el usuario."
    }
    ```

---

## 4. User Login

**Endpoint:** `POST /users/login`

**Description:** Authenticates an existing user and returns a JSON Web Token (JWT).

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
    *   `email` (string, required)
    *   `password` (string, required)

**Response:**
*   **Success (200 OK):**
    ```json
    {
        "access_token": "your_generated_jwt",
        "token_type": "bearer"
    }
    ```
*   **Error (400 Bad Request):** For missing JSON or missing `email`/`password` fields.
    ```json
    {
        "error": "Email y contraseña son requeridos."
    }
    ```
*   **Error (401 Unauthorized):** If credentials are incorrect.
    ```json
    {
        "error": "Credenciales inválidas."
    }
    ```
*   **Error (500 Internal Server Error):**
    ```json
    {
        "error": "Ocurrió un error inesperado al iniciar sesión."
    }
    ```
