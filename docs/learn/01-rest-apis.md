# REST APIs

1. **One-line definition**
A REST API (Representational State Transfer) is a standardized architectural style for networked systems to exchange structured data over standard HTTP methods and URIs.

2. **Why it exists** (the problem it solves)
Before REST, client-server communications relied on disparate, brittle Remote Procedure Calls (RPC) or complex XML protocols (like SOAP) where every application invented its own communication conventions. REST established predictable conventions (GET, POST, PUT, DELETE) and stateless operations, allowing diverse clients (web browsers, mobile apps, other microservices) to talk to any server reliably.

3. **Analogy**
A REST API is like a restaurant menu and waitstaff. The menu defines specific items with clear names (endpoints like `/health` or `/documents`). You give your order using universal verbs ("order", "change", "cancel"), and the waiter handles the kitchen logistics and returns your food without needing to remember what you ate last week (stateless).

4. **How it works** (step by step)
- **Step 1: Request initiation**: The client creates an HTTP request with an HTTP method (`GET`), a URL path (`/health`), optional headers (e.g., `Authorization: Bearer <token>`), and an optional request body.
- **Step 2: Routing**: The server's web framework parses the incoming path and HTTP verb, matching it to the corresponding route handler function.
- **Step 3: Processing & Serialization**: The server processes the request (queries database or runs logic) and serializes the result into a standardized JSON response.
- **Step 4: Response**: The server sends back an HTTP status code (e.g., `200 OK`, `404 Not Found`) along with headers and the JSON response payload.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/main.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/main.py#L38-L62)
- Function: `health_check()` handles `GET /health`.

6. **Common mistakes**
- Using verbs in endpoint paths (e.g., `/getDocuments` or `/deleteUser`) instead of nouns combined with HTTP methods (`GET /documents`, `DELETE /users/{id}`).
- Returning HTTP 200 OK with an error message in the response body instead of returning standard HTTP status codes (`400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`).
- Relying on hidden server session memory rather than making each request self-contained and stateless.

7. **Check yourself**
1. *Which HTTP method should be used to retrieve metadata of a regulatory document without modifying it?*
2. *Why does REST emphasize statelessness between requests?*
3. *What status code should an API return if a requested document ID does not exist in the database?*

---
**Answers:**
1. `GET`.
2. Statelessness ensures each request is self-contained, simplifying horizontal scaling, load balancing, and failure recovery.
3. `404 Not Found`.

