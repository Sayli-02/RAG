# Authentication vs authorization

1. **One-line definition**
Authentication answers “who is this?”. Authorization answers “what is this person allowed to do?”.

2. **Why it exists** (the problem it solves)
A logged-in user is not automatically allowed to do everything. Mixing the two checks makes it easy to protect a route with “has a token” and forget “is this the owner?” or “is this an admin?”.

3. **Analogy**
Authentication is the badge that gets you into the office building. Authorization is the key card that opens only your floor. A valid badge does not open the server room.

4. **How it works** (step by step)
- **Step 1:** Register creates a user with `role="user"`. Login checks the password. That is authentication.
- **Step 2:** A successful login returns a JWT. `/auth/me` reads that token and loads the user. Still authentication: we only learned who they are.
- **Step 3:** Authorization will later read `user.role` or “does this row belong to this user?” before changing documents, chats, or checklists.
- **Step 4:** Phase 1 does not add those checks. No route yet has an admin-only or owner-only action.

5. **Where it is in FinScope** (file + function)
- Authentication: `login` and `read_me` in [backend/app/api/auth.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/api/auth.py), and `get_current_user` in [backend/app/core/dependencies.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/dependencies.py)
- The role value is stored on `User.role` in [backend/app/models/user.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/models/user.py) and set in `register_user`

6. **Common mistakes**
- Calling a 401 “forbidden”. 401 means we do not know who you are (missing or bad token, wrong password). 403 means we know who you are and the action is not allowed.
- Hiding whether an email exists on login, then revealing it on register. Login uses one message for a bad email and a bad password. Register must say the email is taken, or the client cannot correct it.
- Checking the role in the React app only. The API has to check it too, once a route needs it.

7. **Check yourself**
1. *Is rejecting a wrong password authentication or authorization?*
2. *Why does Phase 1 ignore `role` after saving it?*
3. *What should a future “delete someone else’s document” check return if the caller is logged in but is not the owner?*

---
**Answers:**
1. Authentication. The server is still deciding whether these credentials belong to a user.
2. No Phase 1 route behaves differently for `admin` and `user`. The column is there so later routes can check it without a migration.
3. 403 Forbidden. The token is valid, so it is not a 401. The action is not allowed.
