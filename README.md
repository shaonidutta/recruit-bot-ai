# AI Recruitment Agent

An autonomous, multi-agent platform that automates job discovery, intelligence enrichment, candidate-job matching, and personalized outreach for recruitment.

## Project Structure

```
├── services/               # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py        # FastAPI application entry point
│   │   ├── routes/        # API routes
│   │   ├── agents/        # Job scraping agents
│   │   ├── services/      # Business logic services
│   │   ├── workflows/     # LangGraph workflow nodes
│   │   ├── models/        # Data models
│   │   └── config/        # Configuration files
│   ├── Dockerfile         # Services development container
│   └── requirements.txt   # Python dependencies
├── frontend/               # React Vite Frontend
│   ├── src/
│   │   ├── App.jsx        # Root React component
│   │   ├── main.jsx       # Entry point
│   │   └── assets/        # Static assets
│   ├── Dockerfile        # Frontend development container
│   └── package.json      # Frontend dependencies
├── services/              # Python FastAPI Services
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── models.py     # Data models
│   │   ├── routes.py     # API routes
│   │   └── services.py   # Business logic
│   ├── Dockerfile       # Services development container
│   └── requirements.txt # Python dependencies
├── dev.yml              # Development Docker Compose
└── README.md           # Project documentation
```

## Prerequisites

-   Docker and Docker Compose
-   Node.js 20+ (for local development)
-   Python 3.11+ (for local development)

## Development Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-recruitment-agent
```

2. Environment Setup:

    - Create `.env` files in each service directory if needed
    - Backend environment variables:
        ```
        NODE_ENV=development
        SERVICES_URL=http://services:8000
        ```
    - Frontend environment variables:
        ```
        VITE_BACKEND_URL=http://backend:3000
        ```

3. Start the development environment:

```bash
docker compose -f dev.yml up
```

This will start:

-   Frontend: http://localhost:5173
-   Backend: http://localhost:3000
-   Services: http://localhost:8000

## Service Ports

-   Frontend (Vite Dev Server): 5173
-   Backend (Express): 3000
-   Services (FastAPI): 8000

## Local Development

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

### Backend (Node.js + Express)

```bash
cd backend
npm install
npm run dev
```

### Services (Python + FastAPI)

```bash
cd services
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Testing

Each service has its own testing setup:

### Frontend

```bash
cd frontend
npm run lint
```

### Services (Python Backend)

```bash
cd services
python -m pytest
```

## Docker Development

The project uses Docker Compose for development. The `dev.yml` file defines three services:

1. Frontend Container:

    - React development server with hot-reload
    - Mounted volumes for real-time code changes

2. Services Container:
    - Python FastAPI with uvicorn
    - Hot-reload enabled for development
    - AI agents and workflow orchestration

Start all services:

```bash
docker compose -f dev.yml up
```

Build and start specific service:

```bash
docker compose -f dev.yml up --build <service-name>
```

## API Documentation

-   Backend API: http://localhost:3000
-   Services API: http://localhost:8000/docs (Swagger UI)

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

[Add your license information here]
