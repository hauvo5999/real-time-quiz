from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.answer import Answer


class Question(models.Model):
    id = fields.UUIDField(pk=True)
    quiz = fields.ForeignKeyField('models.Quiz', related_name='questions')
    title = fields.CharField(max_length=500)
    description = fields.TextField(null=True)
    image_url = fields.CharField(max_length=500, null=True)
    order = fields.IntField()
    time_limit = fields.IntField(default=30)  # Time limit in seconds
    points = fields.IntField(default=1)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Reverse relations
    # answers: fields.ReverseRelation["Answer"]
    answers: fields.ReverseRelation["Answer"]

    class Meta:
        table = "questions"

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"

# Pydantic models for API
Question_Pydantic = pydantic_model_creator(Question, name="Question")
QuestionIn_Pydantic = pydantic_model_creator(
    Question, name="QuestionIn", exclude_readonly=True
) 