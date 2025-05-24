# API and PostgreSQL Docker Setup

This project contains a Docker Compose configuration for running a Python API server alongside a PostgreSQL database, as well as a Dockerfile for the API service.

---

## Docker Compose Configuration

- **Services:**

  - **server:**  
    - Builds a Python API service from the current directory (`.`).  
    - Maps port `8000` on the host to `8000` inside the container.  
    - Depends on the PostgreSQL database (`db`) and waits until the database service is healthy before starting.

  - **db:**  
    - Uses the official `postgres` image.  
    - Always restarts on failure.  
    - Persists data using a named volume `db-data` to `/var/lib/postgresql/data`.  
    - Sets up the database named `test`.  
    - Uses a database password from the file `db-password.txt` (make sure this file exists and contains your password).  
    - Maps container port `5432` to host port `5433`.  
    - Health check configured with `pg_isready` to ensure the database is ready before the API starts.

- **Volumes:**

  - `db-data`: Stores the PostgreSQL data persistently outside the container lifecycle.

---

## Dockerfile for API Service

- Uses the lightweight Python 3.12.3 slim base image.  
- Sets working directory to `/api`.  
- Copies the project files into the container.  
- Installs required Python packages from `requirements.txt`.  
- Starts the API by running `python3 api.py`.

---

## How to Use

1. Ensure you have Docker and Docker Compose installed.  
2. Create a file `db-password.txt` in the root directory and add your desired PostgreSQL password inside it.  
3. Run the services:

```bash
docker compose up --build
