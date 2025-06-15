# models.py
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum

from app.models.question import Question

class QuizStatus(str, Enum):
    DRAFT = "DRAFT"
    STARTED = "STARTED"
    ENDED = "ENDED"

class Quiz(models.Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(QuizStatus, default=QuizStatus.DRAFT)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Reverse relations
    # questions: fields.ReverseRelation["Question"]
    questions: fields.ReverseRelation["Question"]

    class Meta:
        table = "quizzes"

    def __str__(self):
        return self.title

# Pydantic models for API
Quiz_Pydantic = pydantic_model_creator(Quiz, name="Quiz")
QuizIn_Pydantic = pydantic_model_creator(
    Quiz, name="QuizIn", exclude_readonly=True
)
