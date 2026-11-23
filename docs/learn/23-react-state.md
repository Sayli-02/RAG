# React state and hooks

1. **One-line definition**
State is data a screen remembers between renders. A hook is a function that lets a component keep that data, or run something when it changes.

2. **Why it exists** (the problem it solves)
A login form has to remember what you typed. A document page has to remember the list that came back from the API. If that lived only in a local variable, the next render would forget it.

3. **Analogy**
`useState` is a labeled tray on the desk. You put the email in it, and it is still there after you look away and look back. `useEffect` is a standing instruction: when the tray changes, go fetch the matching file.

4. **How it works** (step by step)
- **Step 1:** `useState` returns the current value and a function that replaces it. Calling that function schedules a new render.
- **Step 2:** Typing in a box calls the setter with `event.target.value`.
- **Step 3:** `useEffect` runs after render. The document detail page uses it to load the document, and to poll again while the status is `processing`.
- **Step 4:** The effect returns a cleanup function so a timer does not fire after you leave the page.

5. **Where it is in FinScope** (file + function)
- Auth tray: `AuthProvider` in [frontend/src/context/AuthContext.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/context/AuthContext.jsx)
- Document list: `load` and the search fields in [frontend/src/pages/Documents.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/pages/Documents.jsx)
- Polling: the effect in [frontend/src/pages/DocumentDetail.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/pages/DocumentDetail.jsx)

6. **Common mistakes**
- Storing the token only in a variable. A refresh would log you out. FinScope also writes it to `localStorage`.
- Forgetting the cleanup on a poll timer. The old page would keep requesting after you navigated away.
- Putting a fetch directly in the component body. It would run on every render and loop.

7. **Check yourself**
1. *What does the setter from `useState` do?*
2. *Why does document detail poll only while the status is processing or uploaded?*
3. *Where does the login token survive a browser refresh?*

---
**Answers:**
1. It stores the new value and asks React to render the component again with that value.
2. Those are the statuses that still change on their own. `indexed` and `failed` are finished, so polling would repeat the same result.
3. `localStorage`, under the key `finscope_token`, written in `login` inside `AuthProvider`.
