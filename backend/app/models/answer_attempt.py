from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum

class AnswerStatus(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    TIMEOUT = "TIMEOUT"
    NOT_ANSWERED = "NOT_ANSWERED"

class AnswerAttempt(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='answer_attempts')
    quiz = fields.ForeignKeyField('models.Quiz', related_name='answer_attempts')
    question = fields.ForeignKeyField('models.Question', related_name='answer_attempts')
    selected_answer = fields.ForeignKeyField('models.Answer', related_name='attempts', null=True)
    status = fields.CharEnumField(AnswerStatus, default=AnswerStatus.NOT_ANSWERED)
    score = fields.IntField(default=0)
    # start_time = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True)
    response_time = fields.IntField(null=True)  # Response time in seconds
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "answer_attempts"
        # Ensure a user can only attempt each question once per quiz
        unique_together = (("user", "quiz", "question"),)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Question {self.question.order}"

    async def calculate_score(self):
        """Calculate the score based on correctness and response time"""
        if self.status == AnswerStatus.CORRECT:
            # Base score from question
            self.score = self.question.points
            
            # Bonus for quick response (if within time limit)
            if self.response_time and self.response_time <= self.question.time_limit:
                time_bonus = int((self.question.time_limit - self.response_time) / 5)
                self.score += time_bonus
        else:
            self.score = 0
        
        await self.save()

# Pydantic models for API
AnswerAttempt_Pydantic = pydantic_model_creator(AnswerAttempt, name="AnswerAttempt")
AnswerAttemptIn_Pydantic = pydantic_model_creator(
    AnswerAttempt, name="AnswerAttemptIn", exclude_readonly=True
) 