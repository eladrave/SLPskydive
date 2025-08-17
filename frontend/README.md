# Skydiving Mentor–Mentee Scheduler

This is a full-stack web application for a skydiving training center to manage mentor availability, mentee attendance, and track progression.

## Tech Stack

- **Backend**: Python, FastAPI, Postgres, SQLAlchemy
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- A web browser

### Running the Application

1.  **Clone the repository.**

2.  **Environment Variables:**
    The application is configured via environment variables. The necessary variables are defined in `docker-compose.yml` for local development. If you need to override them, you can create a `.env` file in the root directory.

3.  **Build and Run with Docker Compose:**
    From the root of the project, run:
    ```bash
    docker-compose up --build
    ```
    This will start three services:
    - `backend`: The FastAPI application, available at `http://localhost:8000`
    - `frontend`: The React application, available at `http://localhost:5173`
    - `db`: The PostgreSQL database.

4.  **Accessing the Application:**
    - **Frontend UI**: Open [http://localhost:5173](http://localhost:5173) in your browser.
    - **Backend API Docs**: The OpenAPI (Swagger) documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Demo Accounts

The database is seeded with initial data on the first run. You can use the following accounts to explore the application:

- **Admin:**
  - Email: `admin@example.com`
  - Password: `admin`
- **Mentor:**
  - Email: `m1@example.com`
  - Password: `password`
- **Mentee:**
  - Email: `e1@example.com`
  - Password: `password`

## Development

### Backend

The backend code is located in `/app/backend`.

To install dependencies (if working outside of Docker):
```bash
pip install -r app/backend/requirements.txt
```

To run backend tests:
```bash
# From the /app/app/backend directory
pytest
```
*Note: The test suite currently has issues related to the execution environment.*

### Frontend

The frontend code is located in `/app/frontend`.

To install dependencies (if working outside of Docker):
```bash
# From the /app/frontend directory
pnpm install
```

To run the frontend dev server:
```bash
# From the /app/frontend directory
pnpm dev
```

To run frontend tests:
```bash
# From the /app/frontend directory
pnpm test
```
*Note: The test runner currently has issues related to the execution environment.*
