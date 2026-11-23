# Docker and Docker Compose

1. **One-line definition**
Docker is an open-source platform that packages applications and their underlying dependencies into lightweight, standalone containers, while Docker Compose coordinates multi-container services with a single configuration file.

2. **Why it exists** (the problem it solves)
The classic "it works on my machine" problem occurs because developer machines have different operating systems, library versions, and system packages installed. Installing complex databases like PostgreSQL with custom extensions (such as `pgvector`) often involves compiling C extensions or configuring host services. Docker packages the exact Linux environment, PostgreSQL binary, and pre-compiled extension into a container that runs identically everywhere with zero host contamination.

3. **Analogy**
Docker containers are like standardized ISO shipping containers. Whether loaded onto a cargo ship, a flatbed train, or a semi-truck, the container locks securely into place without the transport crew needing to know or care what is packed inside. Docker Compose is like the cargo manifest and crane operator, ensuring all interrelated containers are unloaded and connected together in the right order.

4. **How it works** (step by step)
- **Step 1: Image definition**: A container image (e.g. `pgvector/pgvector:pg16`) packages an operating system base, binaries, libraries, and default configurations.
- **Step 2: Compose file specification**: In `docker-compose.yml`, services, environment variables, port mappings (e.g. `5432:5432`), and persistent storage volumes are declared.
- **Step 3: Container instantiation**: Running `docker compose up -d` pulls the required image, sets up virtual network bridges, mounts volumes for data persistence, and starts isolated Linux containers in the background.
- **Step 4: Health checking**: Docker executes periodic probe commands (`pg_isready`) inside the container to report whether the service is ready to accept traffic.

5. **Where it is in FinScope** (file + function)
- Configuration: [docker-compose.yml](file:///c:/Users/Sayli/Downloads/RAG/docker-compose.yml#L1-L20)

6. **Common mistakes**
- Forgetting to declare a persistent volume (`volumes: - postgres_data:...`), resulting in all database records disappearing whenever the container stops or restarts.
- Forgetting port mapping (`5432:5432`), which leaves the database accessible only inside the container's private virtual network and unreachable from the host application.
- Storing hardcoded secrets in version-controlled Compose files instead of reading them from `.env`.

7. **Check yourself**
1. *What happens to database data when a container without a mounted volume is destroyed?*
2. *What does the port mapping `5432:5432` accomplish in Docker Compose?*
3. *Why do we use the specialized `pgvector/pgvector:pg16` image instead of standard `postgres:16`?*

---
**Answers:**
1. All data stored inside the container filesystem is permanently lost.
2. It maps port 5432 of the host machine to port 5432 inside the container, allowing applications on the host (like FastAPI) to communicate with PostgreSQL.
3. The `pgvector/pgvector` image comes with the C-based vector similarity extension already compiled and configured, saving manual compilation steps.

