# API integration

1. **One-line definition**
API integration is the browser calling the FastAPI routes and showing what comes back, including the failures.

2. **Why it exists** (the problem it solves)
The React app does not hold the users, PDFs, or answers. Those live in the API. Every screen has to ask for them, send the login token, and tell you when the API is down.

3. **Analogy**
Axios is the clerk who walks your form to the back office. The interceptor is the stamp the clerk adds to every form: your JWT. You do not rewrite the stamp on each page.

4. **How it works** (step by step)
- **Step 1:** `api` is one Axios client. A request interceptor reads `finscope_token` and sets `Authorization: Bearer …`.
- **Step 2:** Login posts form fields (`username` is the email). Register posts JSON. Upload posts `FormData` with the PDF.
- **Step 3:** A 401 that is not the login attempt clears the token and returns you to `/login`.
- **Step 4:** During `npm run dev`, Vite forwards `/auth`, `/documents`, `/assistant`, and `/health` to port 8000. A normal page load still stays in React, because a browser navigation asks for HTML.

5. **Where it is in FinScope** (file + function)
- Client and errors: `api` and `errorMessage` in [frontend/src/services/api.js](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/services/api.js)
- Proxy: `proxyApi` in [frontend/vite.config.js](file:///c:/Users/Sayli/Downloads/RAG/frontend/vite.config.js)
- Calls: `handleSubmit` in [frontend/src/pages/Login.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/pages/Login.jsx), `handleUpload` in Documents, `handleAsk` in Assistant

6. **Common mistakes**
- Proxying every GET under `/documents`. That path is also a React route, so the browser's first request for the page must not be sent to FastAPI. The proxy skips requests that accept HTML.
- Setting `Content-Type` yourself on a file upload. The browser has to add the multipart boundary. Leaving it unset lets Axios do that.
- Showing a generic error when the server is off. `errorMessage` says the API is not running when the status is 500 or there is no response.

7. **Check yourself**
1. *Which header carries the JWT?*
2. *Why does the login field get sent as `username`?*
3. *What happens if you open `/documents` while logged out?*

---
**Answers:**
1. `Authorization: Bearer <token>`, added by the Axios request interceptor.
2. The backend login route is an OAuth2 form. That form calls the email field `username`.
3. `RequireAuth` in `App.jsx` sends you to `/login`.
