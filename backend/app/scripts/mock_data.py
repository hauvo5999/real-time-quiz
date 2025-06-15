import asyncio
from tortoise import Tortoise
from app.models.user import User
from app.models.quiz import Quiz, QuizStatus
from app.models.question import Question
from app.models.answer import Answer
from app.core.config import TORTOISE_ORM

async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def create_mock_data():
    # Create users
    users = [
        await User.create(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="password123"
        ) for i in range(1, 6)
    ]

    # Create vocabulary quiz
    quiz = await Quiz.create(
        title="English Vocabulary Quiz",
        description="Test your knowledge of English vocabulary with this quiz!",
        status=QuizStatus.DRAFT
    )

    # Vocabulary questions and answers
    vocabulary_data = [
        {
            "question": "What is the meaning of 'ubiquitous'?",
            "answers": [
                {"text": "Present everywhere", "is_correct": True},
                {"text": "Very rare", "is_correct": False},
                {"text": "Extremely large", "is_correct": False},
                {"text": "Completely new", "is_correct": False}
            ]
        },
        {
            "question": "Which word means 'to make something less severe'?",
            "answers": [
                {"text": "Alleviate", "is_correct": True},
                {"text": "Aggravate", "is_correct": False},
                {"text": "Amplify", "is_correct": False},
                {"text": "Accelerate", "is_correct": False}
            ]
        },
        {
            "question": "What is the opposite of 'benevolent'?",
            "answers": [
                {"text": "Malevolent", "is_correct": True},
                {"text": "Benevolent", "is_correct": False},
                {"text": "Excellent", "is_correct": False},
                {"text": "Magnificent", "is_correct": False}
            ]
        },
        {
            "question": "Which word means 'to express strong disapproval'?",
            "answers": [
                {"text": "Condemn", "is_correct": True},
                {"text": "Commend", "is_correct": False},
                {"text": "Comprehend", "is_correct": False},
                {"text": "Compromise", "is_correct": False}
            ]
        },
        {
            "question": "What is the meaning of 'ephemeral'?",
            "answers": [
                {"text": "Lasting for a very short time", "is_correct": True},
                {"text": "Lasting forever", "is_correct": False},
                {"text": "Very important", "is_correct": False},
                {"text": "Extremely valuable", "is_correct": False}
            ]
        }
    ]

    # Create questions and answers
    for i, q_data in enumerate(vocabulary_data, 1):
        question = await Question.create(
            quiz=quiz,
            title=q_data["question"],
            order=i,
            time_limit=30,
            points=1
        )
        
        for j, a_data in enumerate(q_data["answers"], 1):
            await Answer.create(
                question=question,
                text=a_data["text"],
                is_correct=a_data["is_correct"],
                order=j
            )

    print(f"Created {len(users)} users")
    print(f"Created quiz: {quiz.title}")
    print(f"Created {len(vocabulary_data)} questions with answers")

async def main():
    await init()
    await create_mock_data()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main()) 