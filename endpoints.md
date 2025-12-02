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

## 2. Get Current User Profile

**Endpoint:** `GET /users/me`

**Description:** Retrieves the profile information of the currently authenticated user.

**Authentication:** Required. A valid JWT must be provided in the `Authorization` header.

**Request:**
*   **Method:** `GET`
*   **Headers:**
    *   `Authorization: Bearer <your_access_token>`

**Response:**
*   **Success (200 OK):**
    *   **Body:** A single user object.
    ```json
    {
        "data": {
            "id": "293847",
            "name": "Eder",
            "email": "al0293847@example.com",
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

---

## 3. User Signup

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

## 4. User Login

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

## 5. Upload User Avatar

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
    ```json
    {
        "error": "No se encontró el archivo del avatar en la solicitud."
    }
    ```
*   **Error (500 Internal Server Error):** For unexpected issues during the upload process.
    ```json
    {
        "error": "Ocurrió un error desconocido al cambiar el avatar."
    }
    ```