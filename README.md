# 🤖 AI Code Analyzer Platform 🔍

A backend-focused web application that allows users to submit source code, receive structured AI-generated analysis, and manage their past analyses securely.

---

## What This Project Does

This application provides a simple and secure workflow for AI-assisted code analysis:

- Users can register and log in using JWT-based authentication
- Authenticated users can submit source code for analysis
- An AI model analyzes the code and returns structured results (not raw text)
- Each analysis is stored and associated with the submitting user
- Users can view, search, and delete their past analyses
- Ownership and access control are strictly enforced

The project focuses on correctness, simplicity, and production readiness.

---

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: SQLite (local development), PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Templates**: Jinja2
- **Frontend**: HTML with minimal CSS and Bootstrap
- **JavaScript**: Vanilla JavaScript
- **AI Integration**: Groq LLM API with strict JSON-only responses
- **Testing**: Pytest-based integration tests
- **Containerization**: Docker

---

## Project Structure

```bash
AiCodeAnalyzer/
├── alembic/               Database migration scripts and version history
├── static/                Frontend assets
│   └── css/               Basic styling
│   └── js/                Client-side logic (Fetch API, DOM updates)
├── templates/             Jinja2 HTML templates (Dashboard, Auth, History)
├── tests/                 Pytest suite for unit and integration testing
├── ai.py                  Groq API integration and AI prompt/response handling
├── auth.py                JWT generation, hashing, and security
├── database.py            SQLAlchemy engine & session configuration
├── main.py                FastAPI entry point and API routes
├── models.py              SQLAlchemy models (Database tables)
├── schemas.py             Pydantic models (Data validation)
├── Dockerfile             Container definition for the FastAPI application
└── requirements.txt       Python dependencies

```

## Environment Variables

The application requires the following environment variables:

- `DATABASE_URL` — Database connection string  
- `JWT_SECRET` — Secret key used for signing JWTs  
- `ALGORITHM` — HS256 
- `GROQ_API_KEY` — API key for the AI service  

### Local Development
- Environment variables are loaded from a `.env` file
- The `.env` file is **never committed** to version control
- SQLite is used for simplicity

### Production
- Environment variables are injected by the hosting platform
- PostgreSQL is used as the database
- No `.env` file is used in production

---

## Running Locally (Without Docker)



### 1. Download the code file manually or via git

### 2. Create a virtual environment and activate it **(recommended)**

Open your command prompt and change your project directory to ```AiCodeAnalyzer``` and run the following command 
```bash
python -m venv venv

venv/Scripts/activate
```

### 3. Downloading packages from ```requirements.txt```
```bash
pip install -r requirements.txt
```

### 4. After installation is finished create a .```env``` file 

```env
DATABASE_URL=sqlite:///./AiCodeAnalyzerDataBase.db
ALGORITHM=HS256
JWT_SECRET=A_SECRET_KEY
GROQ_API_KEY=YOUR_AI_API_KEY
```
### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Run the FastAPI app

```bash
uvicorn main:app
```

Now the app will be locally available at  ``localhost:8000`` port

---

## Running with Docker

> Note: Docker must be installed and the Docker daemon must be running.

### 1. Build the docker image

```bash
docker build -t ai-code-analyzer .
```

### 2. Run the container

```bash
docker run --env-file .env -p 8000:8000 ai-code-analyzer
```
Now the app will be locally available at  ``localhost:8000`` port

---

## Database and Migrations

- SQLAlchemy is used as the ORM
- Alembic manages all schema migrations
- `Base.metadata.create_all()` is intentionally **not used**
- Migrations must be applied manually when deploying

SQLite is used for development, while PostgreSQL is intended for production.

---

## Testing

- Integration tests only
- Separate test database
- Tests cover authentication, authorization, ownership enforcement, and AI submission flow
- Pytest is used as the test runner

---

## Screenshots

**Login page**

![Screenshot](screenshots/login-page.png?raw=true)

**Code Analysis**

![Screenshot](screenshots/analyzing-page-1.png?raw=true)


![Screenshot](screenshots/analyzing-page-2.png?raw=true)

**History page**

![Screenshot](screenshots/history-page.png?raw=true)


## Deployment Notes

- The application is deployed as a Docker container
- PostgreSQL must be provisioned before deployment
- Alembic migrations must be run once after deployment
- No background workers or task queues are used

---

### Built with 🤍 AiCodeAnalyzer by Asim Roshan