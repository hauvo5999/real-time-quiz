# Real-Time Vocabulary Quiz System

A real-time quiz system built with FastAPI, React, and WebSocket for real-time features.

## System Architecture

![System Architecture](images/image.png)

Currently, the system consists of the following components:

1. **Frontend (React.js)**
   - Real-time quiz interface
   - Live leaderboard
   - User authentication
   - Admin controls

2. **Backend (FastAPI)**
   - RESTful API endpoints
   - WebSocket server for real-time features
   - Database integration
   - Redis for caching and Pub/Sub

3. **Database**
   - PostgreSQL for persistent storage
   - Redis for caching and real-time updates

## Project Structure

```
.
├── frontend/                 # React.js frontend
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── core/            # Core functionality
│   │   └── models/          # Database models
│   ├── main.py
│   └── requirements.txt
│
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

## Setup Instructions

### 1. Database Setup

#### Option 1: Manual Setup
1. Install PostgreSQL and Redis
2. Create a new PostgreSQL database:
   ```bash
   createdb quiz_app
   ```
3. Configure Redis:
   ```bash
   redis-server
   ```

#### Option 2: Docker Compose Setup
1. Create a `docker-compose.yml` file in the root directory:
   ```yaml
   version: '3.8'
   
   services:
     postgres:
       image: postgres:13
       environment:
         POSTGRES_DB: quiz_app
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
     redis:
       image: redis:6
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
   
   volumes:
     postgres_data:
     redis_data:
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. The services will be available at:
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

4. To stop the services:
   ```bash
   docker-compose down
   ```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration:
   ```
   DATABASE_URL=postgres://user:password@localhost:5432/quiz_app
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-secret-key
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at http://localhost:8000

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file:
   ```
   VITE_API_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

### 4. Adding Mock Data (optional)

To populate the system with sample data for testing and development:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the mock data script:
   ```bash
   python scripts/seed_mock_data.py
   ```

This will create:
- Sample quiz questions
- Test user accounts
- Example leaderboard entries

Note: The mock data is for development purposes only and will be reset when the database is reinitialized.

## API Documentation

Once the backend server is running, you can access:
- Swagger UI documentation: http://localhost:8000/api/v1/docs
- ReDoc documentation: http://localhost:8000/api/v1/redoc

## Development

### Backend Development
- Follow PEP 8 style guide
- Use type hints
- Write tests for new features
- Document API endpoints

### Frontend Development
- Follow ESLint rules
- Use TypeScript for type safety
- Write component tests
- Follow Material-UI best practices

<!-- 
## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
``` -->

## Deployment

### Backend Deployment
1. Build Docker image:
   ```bash
   docker build -t quiz-app-backend ./backend
   ```

2. Run container:
   ```bash
   docker run -p 8000:8000 quiz-app-backend
   ```

### Frontend Deployment
1. Build for production:
   ```bash
   cd frontend
   npm run build
   ```

2. Serve the built files using a web server or deploy to a hosting service.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
