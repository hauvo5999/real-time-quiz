from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

class QuizAttempt(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="quiz_attempts")
    quiz = fields.ForeignKeyField("models.Quiz", related_name="attempts")
    score = fields.IntField(default=0)
    started_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "quiz_attempts"

    def __str__(self):
        return f"Attempt by {self.user_id} for Quiz {self.quiz_id}"

# Create Pydantic models
QuizAttempt_Pydantic = pydantic_model_creator(QuizAttempt, name="QuizAttempt")
QuizAttemptIn_Pydantic = pydantic_model_creator(
    QuizAttempt, name="QuizAttemptIn", exclude_readonly=True
) 