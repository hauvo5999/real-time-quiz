# Real-time Quiz API

A FastAPI application with Tortoise ORM for PostgreSQL database.

## Project Structure

```
webserver/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── posts.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── quiz.py
│   │   └── scoring.py
│   │   └── leaderboard.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   └── models/
│       └── models.py
├── main.py
├── requirements.txt
└── .env
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```
Then edit the `.env` file with your configuration.

4. Create the PostgreSQL database:
```bash
createdb perfume_blog
```

## Running the Application

Start the server:
```bash
uvicorn main:app --reload
```
or 
```bash
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: http://localhost:8000/api/v1/docs
- ReDoc documentation: http://localhost:8000/api/v1/redoc

## Available Endpoints

### Users
- `POST /api/v1/users/`: Create a new user
- `GET /api/v1/users/`: List all users
- `GET /api/v1/users/{user_id}`: Get a specific user

### Posts
- `POST /api/v1/posts/`: Create a new post
- `GET /api/v1/posts/`: List all posts
- `GET /api/v1/posts/{post_id}`: Get a specific post 