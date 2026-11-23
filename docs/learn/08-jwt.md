# JWT (JSON Web Token)

1. **One-line definition**
A JWT is a signed string the server gives you after login. Later requests show that string to prove who you are.

2. **Why it exists** (the problem it solves)
After login, the server needs to recognize you on the next request without storing a session row for every visit. The token carries the user id and an expiry, and a secret signature proves the server created it.

3. **Analogy**
It is a concert wristband. The door staff stamp it. You show the band at each room. They do not keep a clipboard of your name, but a torn or forged band is rejected.

4. **How it works** (step by step)
- **Step 1:** Login checks email and password. On success, `create_access_token` builds a payload: `sub` is the user id, `exp` is 60 minutes from now.
- **Step 2:** PyJWT signs that payload with `JWT_SECRET_KEY` using HS256. The signature is the third part of the token.
- **Step 3:** The client sends `Authorization: Bearer <token>` on later requests.
- **Step 4:** `decode_access_token` checks the signature and expiry. `get_current_user` loads that user from the database. A bad, expired, or missing token returns 401.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/core/security.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/security.py)
- `create_access_token` and `decode_access_token`
- File: [backend/app/core/dependencies.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/dependencies.py)
- `get_current_user`
- Issued by `login` in [backend/app/api/auth.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/api/auth.py)

6. **Common mistakes**
- Putting the secret in source code. FinScope reads `JWT_SECRET_KEY` from `.env` and refuses to start if it is missing.
- Trusting the token without checking the signature, or accepting more than one algorithm. Decode allows only HS256.
- Treating the token as encrypted. Anyone can read the payload. Do not put secrets in it. It only holds the user id and expiry.

7. **Check yourself**
1. *What stops someone from changing the user id inside the token?*
2. *Why does `/auth/me` still look up the user in the database?*
3. *Which endpoints work without a token?*

---
**Answers:**
1. The signature was made with the server secret. Changing the payload breaks the signature, and `decode_access_token` raises `ValueError`.
2. The token says which id was logged in. The database row is still the source of the name, email, and role, and a deleted user must not keep working.
3. `GET /health`, `POST /auth/register`, and `POST /auth/login`. Every other route is expected to require a JWT.
