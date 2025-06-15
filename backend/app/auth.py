from fastapi import WebSocket, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user_ws(websocket: WebSocket) -> User:
    """
    Simple username-based authentication
    """
    try:
        # Get username from query parameters
        username = websocket.query_params.get("username")
        print(f"Username: {username}")
        if not username:
            raise HTTPException(status_code=401, detail="Username is required")
        
        # Find or create user by username
        user, _ = await User.get_or_create(username=username)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Original authentication code (commented out)
"""
async def get_current_user_ws(websocket: WebSocket) -> User:
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001)
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Decode token
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=4001)
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await User.get_or_none(id=user_id)
        if user is None:
            await websocket.close(code=4001)
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        await websocket.close(code=4001)
        raise HTTPException(status_code=401, detail="Invalid token") 
"""