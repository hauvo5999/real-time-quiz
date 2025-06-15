from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

class Leaderboard(models.Model):
    id = fields.UUIDField(pk=True)
    quiz_id = fields.UUIDField()
    user_id = fields.UUIDField()
    score = fields.IntField(default=0)
    rank = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "leaderboards"
        indexes = (("quiz_id", "user_id"), ("quiz_id", "score"))

    def __str__(self):
        return f"Leaderboard {self.id} - Quiz: {self.quiz_id} - User: {self.user_id}"

# Create Pydantic models
Leaderboard_Pydantic = pydantic_model_creator(Leaderboard, name="Leaderboard")
LeaderboardIn_Pydantic = pydantic_model_creator(
    Leaderboard, name="LeaderboardIn", exclude_readonly=True
) 