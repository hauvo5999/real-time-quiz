from fastapi import FastAPI
from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.database import init_db
from app.websocket.v1.websocket import router as websocket_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Real-Time Quiz API - A RESTful API for managing real-time quiz content.
    
    ## Features
    * User management
    * Quiz management
    * Authentication (coming soon)
    
    ## Authentication
    Authentication will be implemented in future versions.
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_tags=[
        {
            "name": "users",
            "description": "Operations with users. The **users** tag allows you to manage users in the system.",
        },
    ],
)

# Initialize database
init_db(app)

# Include v1 API router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(websocket_router)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 