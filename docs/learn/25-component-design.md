# Component design

1. **One-line definition**
A component is a piece of the screen with its own markup and props, used wherever that piece repeats.

2. **Why it exists** (the problem it solves)
The citation under an answer has a fixed shape: title, authority, page, section, excerpt. Writing that block once means the chat and any later screen stay the same when the shape changes.

3. **Analogy**
It is a rubber stamp. The page decides where to press it. The stamp decides what the impression looks like.

4. **How it works** (step by step)
- **Step 1:** `CitationCard` receives one citation object and renders the fields. It does not fetch anything.
- **Step 2:** `Assistant` maps the citations on an assistant message and renders one card each.
- **Step 3:** `Sidebar` is the other shared piece: the wordmark, Documents, Assistant, and Log out. `AppShell` puts it beside whatever page is current.
- **Step 4:** Pages own the buttons and the API calls. Components own how a repeated thing looks.

5. **Where it is in FinScope** (file + function)
- Citation: `CitationCard` in [frontend/src/components/assistant/CitationCard.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/components/assistant/CitationCard.jsx)
- Shell: `Sidebar` in [frontend/src/components/common/Sidebar.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/components/common/Sidebar.jsx) and `AppShell` in [frontend/src/layouts/AppShell.jsx](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/layouts/AppShell.jsx)
- Pages: [frontend/src/pages/](file:///c:/Users/Sayli/Downloads/RAG/frontend/src/pages)

6. **Common mistakes**
- Fetching inside a card. The card then cannot be reused with data you already have.
- Copying the sidebar into each page. A route change would have to be edited in every file.
- Making one giant component for the whole app. Login, the library, and the chat would all re-render together and be harder to read.

7. **Check yourself**
1. *What props does `CitationCard` need?*
2. *Which component logs you out?*
3. *Why is the upload form inside `Documents` rather than its own card component?*

---
**Answers:**
1. A `citation` object with title, authority, page, section, and excerpt.
2. `Sidebar`. Its Log out button calls `logout` from `useAuth` and sends you to `/login`.
3. The form is used in one place and owns the upload request. A separate component would only move that one form into another file.
