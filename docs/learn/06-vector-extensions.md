# Vector Extensions and pgvector

1. **One-line definition**
`pgvector` is an open-source PostgreSQL extension that introduces a specialized vector data type and distance operators to enable high-dimensional vector similarity search alongside traditional relational data.

2. **Why it exists** (the problem it solves)
Traditional databases excel at exact matches, numeric comparisons, and basic text searches. However, AI applications rely on high-dimensional vector embeddings—numerical arrays that capture semantic meaning. Dedicated vector databases (like Pinecone or Milvus) require maintaining a separate database system, duplicating data, and dealing with distributed data synchronization. `pgvector` brings vector similarity search directly into PostgreSQL, allowing developers to query vectors and join them with relational metadata (like `authority = 'RBI'` or `publication_date >= '2024-01-01'`) in a single ACID transaction.

3. **Analogy**
Imagine a library. Traditional database indexing is like organizing books alphabetically by author and ISBN number. Vector embeddings are like positioning books in a multi-dimensional space where books about similar topics (e.g., credit card regulation, payment security) float close together in space regardless of author name. `pgvector` is the 3D positioning and distance measurement system that measures which books are physically closest to your query.

4. **How it works** (step by step)
- **Step 1: Extension enablement**: The command `CREATE EXTENSION IF NOT EXISTS vector;` registers the `vector(N)` type in PostgreSQL where `N` is the fixed dimensionality.
- **Step 2: Vector column creation**: In `document_chunks`, a column is declared as `embedding Vector(384)` to store dense embeddings.
- **Step 3: Distance metric calculation**: When searching, vector distance operators calculate proximity:
  - `<->`: Euclidean (L2) distance
  - `<=>`: Cosine distance (most common for text embeddings)
  - `<#>`: Negative inner product
- **Step 4: Index acceleration**: High-dimensional search over large datasets uses Approximate Nearest Neighbor (ANN) index algorithms such as HNSW (Hierarchical Navigable Small World) or IVFFlat to retrieve top-k closest vectors in milliseconds without scanning the entire table.

5. **Where it is in FinScope** (file + function)
- Configuration: [backend/app/core/config.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/config.py#L25) (`VECTOR_DIMENSION = 384`)
- Model definition: [backend/app/models/document.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/models/document.py#L74) (`embedding = mapped_column(Vector(settings.VECTOR_DIMENSION))`)
- Migration: [backend/alembic/versions/0001_initial_schema.py](file:///c:/Users/Sayli/Downloads/RAG/backend/alembic/versions/0001_initial_schema.py#L19) (`CREATE EXTENSION IF NOT EXISTS vector;`)

6. **Common mistakes**
- Mismatching dimensions: generating embeddings with a 768-dimensional model and attempting to insert them into a `Vector(384)` column, which throws a database error.
- Normalization oversight: failing to normalize vectors when computing cosine distance or dot products.
- Forgetting to build an HNSW index when chunk volume scales, causing slow sequential full-table vector distance scans.

7. **Check yourself**
1. *What operator is used in pgvector to calculate cosine distance?*
2. *Why is storing embeddings in PostgreSQL with pgvector advantageous over a separate standalone vector database?*
3. *What happens if you try to insert an embedding with 512 dimensions into a `Vector(384)` column?*

---
**Answers:**
1. The `<=>` operator.
2. It eliminates the operational complexity of managing two distinct databases, maintains ACID transactions, and enables single-query filtering combining structured metadata with semantic similarity.
3. PostgreSQL rejects the insert with a dimension mismatch error.

