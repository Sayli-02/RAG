# Split deployment

1. **One-line definition**
Split deployment runs the website, the API, and the database as three separate hosted services.

2. **Why it exists** (the problem it solves)
The Vite dev server pretends the API is on the same origin. A public site cannot do that. The browser loads static files from one host and must be told the real API address. The API must be told which website is allowed to call it.

3. **Analogy**
The shop window is on one street (Vercel). The workshop is on another (Render or Railway). The filing cabinet is in a third building (Supabase). The window has the workshop's address printed on it, and the workshop only opens the door for that window.

4. **How it works** (step by step)
- **Step 1:** Supabase hosts Postgres with pgvector. `SQLALCHEMY_DATABASE_URI` is the session-pooler URI, scheme `postgresql+psycopg2`, port 5432.
- **Step 2:** Render or Railway runs `alembic upgrade head` and then uvicorn. `CORS_ORIGINS` lists the Vercel site. The JWT stays in the Authorization header.
- **Step 3:** Vercel builds the React app with `VITE_API_URL` set to the API origin. Axios uses that as `baseURL`. A rewrite sends every path to `index.html` so a refresh of `/documents` still opens the app.
- **Step 4:** Changing `VITE_API_URL` requires a new Vercel build. Changing `CORS_ORIGINS` requires a new API deploy.

5. **Where it is in FinScope** (file + function)
- `cors_origin_list` in `backend/app/core/config.py`, used by the CORS middleware in `backend/app/main.py`
- `baseURL` in `frontend/src/services/api.js`
- `frontend/vercel.json`, `render.yaml`, and `backend/railway.toml`

6. **Common mistakes**
- Using the Supabase transaction pooler (port 6543). Alembic loses the session between statements.
- Leaving `VITE_API_URL` empty on Vercel. The browser then calls the Vercel host for `/auth/login` and gets the HTML app instead of JSON.
- Forgetting to add the Vercel URL to `CORS_ORIGINS`. The browser blocks the response.

7. **Check yourself**
1. *Which host serves the React files?*
2. *Which URI port should Supabase use for this app?*
3. *When does a change to `VITE_API_URL` take effect?*

## Answers
1. Vercel.
2. 5432, the session pooler.
3. On the next Vercel build.
