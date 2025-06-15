from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Answer(models.Model):
    id = fields.UUIDField(pk=True)
    question = fields.ForeignKeyField('models.Question', related_name='answers')
    text = fields.CharField(max_length=500)
    is_correct = fields.BooleanField(default=False)
    order = fields.IntField()  # For ordering options (A, B, C, D)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "answers"

    def __str__(self):
        return f"{self.question.title} - Option {self.order}"

# Pydantic models for API
Answer_Pydantic = pydantic_model_creator(Answer, name="Answer")
AnswerIn_Pydantic = pydantic_model_creator(
    Answer, name="AnswerIn", exclude_readonly=True
) 