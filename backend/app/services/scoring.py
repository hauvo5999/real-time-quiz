from typing import List, Dict
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.answer_attempt import AnswerAttempt
from app.core.redis import get_redis
import json

class ScoringService:
    def __init__(self):
        self.REDIS_EXPIRATION_TIME = 60 * 5  # 5 minutes
        self.USER_SCORE_KEY = "quiz:{quiz_id}:user:{username}:score"
        self.USER_QUESTIONS_KEY = "quiz:{quiz_id}:user:{username}:questions"
        self.QUIZ_QUESTIONS_KEY = "quiz:{quiz_id}:questions"

    async def initialize_user_score(self, quiz_id: str, username: str) -> None:
        """Initialize user score in Redis"""
        redis = await get_redis()
        score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=username)
        if not await redis.exists(score_key):
            await redis.set(score_key, 0, ex=self.REDIS_EXPIRATION_TIME)

    async def initialize_user_questions(self, quiz_id: str, username: str) -> None:
        """Initialize user questions in Redis"""
        redis = await get_redis()
        questions_key = self.USER_QUESTIONS_KEY.format(quiz_id=quiz_id, username=username)
        if not await redis.exists(questions_key):
            await redis.set(questions_key, json.dumps([]), ex=self.REDIS_EXPIRATION_TIME)

    async def initialize_quiz_questions(self, quiz_id: str) -> None:
        """Initialize quiz questions in Redis"""
        redis = await get_redis()
        quiz_questions_key = self.QUIZ_QUESTIONS_KEY.format(quiz_id=quiz_id)
        if not await redis.exists(quiz_questions_key):
            questions = await Question.filter(quiz_id=quiz_id).order_by('order')
            questions_data = [str(q.id) for q in questions]
            await redis.set(quiz_questions_key, json.dumps(questions_data), ex=self.REDIS_EXPIRATION_TIME)

    async def check_answer(self, question_id: int, answer_id: int) -> bool:
        """Check if answer is correct"""
        try:
            answer = await Answer.get_or_none(id=answer_id, question_id=question_id)
            return answer and answer.is_correct
        except Exception as e:
            print(f"Error checking answer: {str(e)}")
            return False

    async def update_user_score(self, quiz_id: str, username: str, adding_score: int = 0) -> None:
        """Update user score in Redis"""
        redis = await get_redis()
        score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=username)
        current_score = int(await redis.get(score_key) or 0)
        await redis.set(score_key, current_score + adding_score, ex=self.REDIS_EXPIRATION_TIME)

    async def add_answered_question(self, quiz_id: str, username: str, question_id: int) -> None:
        """Add question to answered questions in Redis"""
        redis = await get_redis()
        questions_key = self.USER_QUESTIONS_KEY.format(quiz_id=quiz_id, username=username)
        answered_questions = json.loads(await redis.get(questions_key) or "[]")
        if question_id not in answered_questions:
            answered_questions.append(question_id)
            await redis.set(questions_key, json.dumps(answered_questions), ex=self.REDIS_EXPIRATION_TIME)

    async def get_user_score(self, quiz_id: str, username: str) -> int:
        """Get user's current score"""
        redis = await get_redis()
        score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=username)
        return int(await redis.get(score_key) or 0)

    async def get_answered_questions(self, quiz_id: str, username: str) -> List[int]:
        """Get list of answered questions"""
        redis = await get_redis()
        questions_key = self.USER_QUESTIONS_KEY.format(quiz_id=quiz_id, username=username)
        return json.loads(await redis.get(questions_key) or "[]")

    async def get_quiz_questions(self, quiz_id: str) -> List[str]:
        """Get all quiz questions"""
        redis = await get_redis()
        quiz_questions_key = self.QUIZ_QUESTIONS_KEY.format(quiz_id=quiz_id)
        return json.loads(await redis.get(quiz_questions_key) or "[]")

    async def clear_user_data(self, quiz_id: str, username: str) -> None:
        """Clear user's quiz data from Redis"""
        redis = await get_redis()
        score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=username)
        questions_key = self.USER_QUESTIONS_KEY.format(quiz_id=quiz_id, username=username)
        await redis.delete(score_key, questions_key)

    async def clear_answer_attempts(self, quiz_id: str, user_id: str) -> None:
        """Clear answer attempts for a user"""
        try:
            await AnswerAttempt.filter(quiz_id=quiz_id, user_id=user_id).delete()
            username = (await User.get_or_none(id=user_id)).username
            redis = await get_redis()
            score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=username)
            await redis.delete(score_key)
        except Exception as e:
            print(f"Error clearing answer attempts: {str(e)}")

# Create a singleton instance
scoring_service = ScoringService()
