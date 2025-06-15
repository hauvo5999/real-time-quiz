from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.core.redis import get_redis
from app.services.scoring import scoring_service
from app.services.leaderboard import leaderboard_service
import json
from app.auth import get_current_user_ws

REDIS_EXPIRATION_TIME = 60 * 5  # 5 minutes

router = APIRouter(prefix="/ws")

# Store active connections
active_connections: Dict[str, List[WebSocket]] = {}

# Redis key patterns
USER_SCORE_KEY = "quiz:{quiz_id}:user:{username}:score"
USER_QUESTIONS_KEY = "quiz:{quiz_id}:user:{username}:questions"
QUIZ_QUESTIONS_KEY = "quiz:{quiz_id}:questions"

@router.websocket("/quiz/{quiz_id}", "Join a quiz")
async def initialize_joining_quiz(websocket: WebSocket, quiz_id: str):
    await websocket.accept()
    
    try:
        # Get current user from websocket
        user = await get_current_user_ws(websocket)
        
        # Get quiz
        quiz = await Quiz.get_or_none(id=quiz_id)
        if not quiz:
            await websocket.close(code=4004, reason="Quiz not found")
            return
        
        # Add connection to active connections
        if quiz_id not in active_connections:
            active_connections[quiz_id] = []
        active_connections[quiz_id].append(websocket)

        await leaderboard_service.subscribe(quiz_id, websocket)

        # Initialize user data in Redis
        await scoring_service.initialize_user_score(quiz_id, user.username)
        await scoring_service.initialize_user_questions(quiz_id, user.username)
        await scoring_service.initialize_quiz_questions(quiz_id)

        await scoring_service.clear_answer_attempts(quiz_id, user.id)
        
        # Send initial question
        await send_next_question(websocket, quiz_id, user)

        # Subscribe to leaderboard updates
        await leaderboard_service.join_leaderboard(quiz_id, user)
        # Send initial leaderboard
        await leaderboard_service.broadcast_leaderboard(quiz_id, active_connections)

        # Handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "submit_answer":
                    await handle_answer_submission(
                        websocket, quiz_id, user, message["data"]["question_id"], message["data"]["answer_id"]
                    )
                elif message["type"] == "request_next_question":
                    await send_next_question(websocket, quiz_id, user)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error handling message: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in join_quiz: {str(e)}")
        await websocket.close(code=4000, reason=str(e))
    finally:
        # Remove connection from active connections
        if quiz_id in active_connections:
            active_connections[quiz_id].remove(websocket)
            if not active_connections[quiz_id]:
                del active_connections[quiz_id]
        
        # Unsubscribe from leaderboard updates
        leaderboard_service.unsubscribe(quiz_id, websocket)
        
        await websocket.close()

async def handle_answer_submission(websocket: WebSocket, quiz_id: str, user: User, question_id: int, answer_id: int):
    """Handle answer submission and update score"""
    try:
        # Check if answer is correct
        is_correct = await scoring_service.check_answer(question_id, answer_id)

        # TODO: Handle more complex scoring logic
        score = 1 if is_correct else 0

        # Update score and answered questions
        await scoring_service.update_user_score(quiz_id, user.username, score)
        await scoring_service.add_answered_question(quiz_id, user.username, question_id)
    
        if is_correct:
            # Send success message
            await websocket.send_text(json.dumps({
                "type": "answer_result",
                "data": {
                    "correct": True,
                    "message": "Correct answer!"
                }
            }))
            
            # Broadcast updated leaderboard using leaderboard service
            await leaderboard_service.broadcast_leaderboard(quiz_id, active_connections)
        else:
            # Send failure message
            await websocket.send_text(json.dumps({
                "type": "answer_result",
                "data": {
                    "correct": False,
                    "message": "Incorrect answer!"
                }
            }))

    except Exception as e:
        print(f"Error handling answer submission: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": {
                "message": "Error processing answer"
            }
        }))

async def send_next_question(websocket: WebSocket, quiz_id: str, user: User):
    """Send next unanswered question to user"""
    try:
        # Get all quiz questions and answered questions
        all_questions = await scoring_service.get_quiz_questions(quiz_id)
        answered_questions = await scoring_service.get_answered_questions(quiz_id, user.username)
        
        # Find next unanswered question
        next_question_id = None
        for q_id in all_questions:
            if q_id not in answered_questions:
                next_question_id = q_id
                break
        
        if next_question_id:
            # Get question data
            question = await Question.get_or_none(id=next_question_id)
            if question:
                answers = await Answer.filter(question_id=question.id)
                
                # Send question data
                await websocket.send_text(json.dumps({
                    "type": "question",
                    "data": {
                        "id": str(question.id),
                        "text": question.title,
                        "time_limit": question.time_limit,
                        "answers": [
                            {
                                "id": str(answer.id),
                                "text": answer.text
                            }
                            for answer in answers
                        ]
                    }
                }))
        else:
            # No more questions
            await websocket.send_text(json.dumps({
                "type": "quiz_complete",
                "data": {
                    "message": "You have completed all questions!"
                }
            }))
            # Clear user data
            # await scoring_service.clear_user_data(quiz_id, user.username)
            
    except Exception as e:
        print(f"Error sending next question: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": {
                "message": "Error getting next question"
            }
        }))

async def broadcast_leaderboard(quiz_id: str):
    """Broadcast leaderboard to all connected clients"""
    await leaderboard_service.broadcast_leaderboard(quiz_id, active_connections)
