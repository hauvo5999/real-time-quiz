from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class LeaderboardBase(BaseModel):
    quiz_id: UUID4
    user_id: UUID4
    score: int = 0
    rank: int = 0

class LeaderboardCreate(LeaderboardBase):
    pass

class LeaderboardUpdate(LeaderboardBase):
    score: Optional[int] = None
    rank: Optional[int] = None

class LeaderboardInDB(LeaderboardBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeaderboardResponse(LeaderboardInDB):
    username: str  # We'll join this from the user model

class LeaderboardList(BaseModel):
    items: List[LeaderboardResponse]
    total: int
    quiz_id: UUID4

# WebSocket message schemas
class LeaderboardUpdateMessage(BaseModel):
    type: str = "leaderboard_update"
    quiz_id: UUID4
    leaderboard: List[LeaderboardResponse] 