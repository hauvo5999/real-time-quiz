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


async def create_users():
    users = [
        await User.create(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="password123"
        ) for i in range(1, 6)
    ]
    print(f"Created {len(users)} users")

async def create_vocabulary_quiz_data():
    vocab_quiz = await Quiz.create(
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

     # Create questions and answers for vocabulary quiz
    for i, q_data in enumerate(vocabulary_data, 1):
        question = await Question.create(
            quiz=vocab_quiz,
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
    print(f"Created quiz: {vocab_quiz.title}")
    print(f"Created {len(vocabulary_data)} vocabulary questions with answers")
    

async def create_general_knowledge_quiz_data():
    general_quiz = await Quiz.create(
        title="General Knowledge Quiz",
        description="Test your knowledge of various topics with this quiz!",
        status=QuizStatus.DRAFT
    )

    # General knowledge questions and answers
    general_data = [
        {
            "question": "What is the capital of Japan?",
            "answers": [
                {"text": "Tokyo", "is_correct": True},
                {"text": "Kyoto", "is_correct": False},
                {"text": "Osaka", "is_correct": False},
                {"text": "Nagoya", "is_correct": False}
            ]
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "answers": [
                {"text": "Mars", "is_correct": True},
                {"text": "Venus", "is_correct": False},
                {"text": "Jupiter", "is_correct": False},
                {"text": "Saturn", "is_correct": False}
            ]
        },
        {
            "question": "What is the largest ocean on Earth?",
            "answers": [
                {"text": "Pacific Ocean", "is_correct": True},
                {"text": "Atlantic Ocean", "is_correct": False},
                {"text": "Indian Ocean", "is_correct": False},
                {"text": "Arctic Ocean", "is_correct": False}
            ]
        },
        {
            "question": "Who painted the Mona Lisa?",
            "answers": [
                {"text": "Leonardo da Vinci", "is_correct": True},
                {"text": "Vincent van Gogh", "is_correct": False},
                {"text": "Pablo Picasso", "is_correct": False},
                {"text": "Michelangelo", "is_correct": False}
            ]
        },
        {
            "question": "What is the chemical symbol for gold?",
            "answers": [
                {"text": "Au", "is_correct": True},
                {"text": "Ag", "is_correct": False},
                {"text": "Fe", "is_correct": False},
                {"text": "Cu", "is_correct": False}
            ]
        },
        {
            "question": "Which country is home to the kangaroo?",
            "answers": [
                {"text": "Australia", "is_correct": True},
                {"text": "New Zealand", "is_correct": False},
                {"text": "South Africa", "is_correct": False},
                {"text": "Brazil", "is_correct": False}
            ]
        },
        {
            "question": "What is the largest organ in the human body?",
            "answers": [
                {"text": "Skin", "is_correct": True},
                {"text": "Liver", "is_correct": False},
                {"text": "Heart", "is_correct": False},
                {"text": "Brain", "is_correct": False}
            ]
        },
        {
            "question": "Which element has the chemical symbol 'O'?",
            "answers": [
                {"text": "Oxygen", "is_correct": True},
                {"text": "Osmium", "is_correct": False},
                {"text": "Oganesson", "is_correct": False},
                {"text": "Osmium", "is_correct": False}
            ]
        },
        {
            "question": "What is the currency of the United Kingdom?",
            "answers": [
                {"text": "British Pound", "is_correct": True},
                {"text": "Euro", "is_correct": False},
                {"text": "Dollar", "is_correct": False},
                {"text": "Yen", "is_correct": False}
            ]
        },
        {
            "question": "Which famous scientist developed the theory of relativity?",
            "answers": [
                {"text": "Albert Einstein", "is_correct": True},
                {"text": "Isaac Newton", "is_correct": False},
                {"text": "Galileo Galilei", "is_correct": False},
                {"text": "Stephen Hawking", "is_correct": False}
            ]
        }
    ]


    # Create questions and answers for general knowledge quiz
    for i, q_data in enumerate(general_data, 1):
        question = await Question.create(
            quiz=general_quiz,
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

    print(f"Created quiz: {general_quiz.title}")
    print(f"Created {len(general_data)} general knowledge questions with answers")
    

async def create_mock_data():
    # Create users
    # await create_users()

    # Create vocabulary quiz
    # await create_vocabulary_quiz_data()

    # Create general knowledge quiz
    await create_general_knowledge_quiz_data()

async def main():
    await init()
    await create_mock_data()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main()) 