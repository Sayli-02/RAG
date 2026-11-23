# Object-Relational Mapping (ORM) and SQLAlchemy

1. **One-line definition**
An Object-Relational Mapping (ORM) is a software pattern and library that allows developers to query and manipulate relational database tables using object-oriented code instead of raw SQL strings.

2. **Why it exists** (the problem it solves)
Writing raw SQL strings directly in application code is error-prone, hard to refactor, vulnerable to SQL injection attacks, and tightly couples application code to a specific database vendor's SQL syntax. An ORM provides type-safe abstractions, manages transactions, auto-escapes user input, and maps database rows directly into Python objects.

3. **Analogy**
An ORM is like a translator and personal concierge between two people who speak different languages: Python (which thinks in objects, classes, and references) and PostgreSQL (which thinks in rows, tables, and foreign keys). You speak Python to the translator, and the translator communicates fluently in SQL with the database.

4. **How it works** (step by step)
- **Step 1: Declarative Base**: A base class (`class Base(DeclarativeBase)`) maintains a catalog of all model classes and their metadata.
- **Step 2: Model definition**: Python classes represent tables (e.g., `class Document(Base)`), where class attributes map to columns (`title = mapped_column(String(500))`) and foreign-key relationships.
- **Step 3: Engine & Session**: An engine manages physical network connections to the database pool. A `Session` acts as a staging area (unit of work) that tracks changes to objects.
- **Step 4: Query translation**: When you query or commit (`session.add(doc); session.commit()`), SQLAlchemy generates parameterized SQL statements, sends them to the database engine, and transforms the returned tabular records into Python model instances.

5. **Where it is in FinScope** (file + function)
- Declarative Base: [backend/app/database/base.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/database/base.py#L4-L6)
- Session factory & `get_db`: [backend/app/database/session.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/database/session.py#L7-L22)
- Models: [backend/app/models/document.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/models/document.py#L18-L96) (`Document`, `DocumentVersion`, `DocumentChunk`)

6. **Common mistakes**
- Falling into the "N+1 query problem": fetching a list of parent rows and then querying the database individually for each child relationship in a loop instead of eager loading (`joinedload` or `selectinload`).
- Sharing a single SQLAlchemy `Session` instance across multiple concurrent threads or requests rather than creating a fresh session per request.
- Forgetting to call `session.commit()` after mutating records, causing transactions to be rolled back when the session closes.

7. **Check yourself**
1. *What is the difference between an SQLAlchemy Engine and a Session?*
2. *How does an ORM protect applications from SQL injection attacks?*
3. *Why do we define relationships (e.g. `relationship("DocumentChunk", back_populates="document")`) in addition to foreign keys?*

---
**Answers:**
1. The Engine manages low-level database connection pooling and raw dialect communication; the Session is an in-memory workspace that tracks object state, executes queries, and manages transactions.
2. The ORM uses parameterized queries where data inputs are sent separately from SQL command syntax, preventing malicious input from modifying the SQL query structure.
3. Foreign keys enforce referential integrity at the database level, while relationships allow Python code to navigate seamlessly between connected objects (e.g., accessing `doc.chunks` directly as a Python list).

