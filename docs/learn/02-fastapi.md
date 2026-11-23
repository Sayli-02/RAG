# FastAPI

1. **One-line definition**
FastAPI is a modern, high-performance Python web framework for building APIs with type hints, automated data validation via Pydantic, and native asynchronous support.

2. **Why it exists** (the problem it solves)
Older Python web frameworks (like Flask or Django) required significant boilerplate to validate request data, parse query/body parameters, handle asynchronous I/O, and maintain API documentation. If an endpoint expected an integer and received a string, developers had to write manual validation code. FastAPI solves this by leveraging standard Python 3 type hints to automatically validate inputs, convert data types, handle concurrency via `async`/`await`, and generate interactive OpenAPI (Swagger) docs automatically.

3. **Analogy**
FastAPI is like an airport customs checkpoint equipped with automated biometric e-gates. Rather than an agent manually inspecting every passport page and verifying visa requirements with paper stamps, the automated gate checks your document against precise specifications instantly, rejects invalid travelers immediately with clear reasons, and logs your passage automatically.

4. **How it works** (step by step)
- **Step 1: Application initialization**: The FastAPI application instance is created with project metadata (title, version, description) and lifespan event managers.
- **Step 2: Route declaration**: Endpoints are defined using decorators (e.g., `@app.get("/health")`) with type-annotated parameters and return types.
- **Step 3: Dependency Injection**: When a request arrives, FastAPI inspects declared dependencies (`Depends(get_db)`), resolves them, and injects the results into the route handler function.
- **Step 4: Serialization & Documentation**: The handler's return value is validated and serialized according to the declared Pydantic schema (`response_model`), and exposed on the interactive documentation page (`/docs`).

5. **Where it is in FinScope** (file + function)
- File: [backend/app/main.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/main.py#L22-L36)
- App instance: `app = FastAPI(...)`
- File: [backend/app/schemas/health.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/schemas/health.py#L4-L10)
- Schema: `HealthCheckResponse(BaseModel)`

6. **Common mistakes**
- Mixing blocking synchronous database calls inside `async def` endpoints, which blocks FastAPI's event loop; use regular `def` for standard synchronous calls (SQLAlchemy sync sessions) or use `async def` with an async database driver.
- Forgetting to define or update `response_model`, resulting in leaking internal fields or bypassing output filtering.
- Not cleaning up resources created in dependencies; always use `yield` in a generator dependency with a `finally:` block.

7. **Check yourself**
1. *How does FastAPI generate automatic Swagger documentation?*
2. *What happens when a client sends invalid data types to an endpoint expecting a Pydantic schema?*
3. *Why should a dependency providing a database session use `yield` instead of a simple `return`?*

---
**Answers:**
1. FastAPI inspects the Python type hints and Pydantic schemas declared on routes to produce an OpenAPI JSON specification, which Swagger UI renders at `/docs`.
2. FastAPI automatically catches the error and returns a `422 Unprocessable Entity` response detailing which field was invalid and why.
3. Using `yield` allows execution to pause while the endpoint runs, and resume in the `finally` block after the response is sent to guarantee the database connection is closed.

