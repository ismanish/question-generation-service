"""
Question generation API routes
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any

from src.models.schemas import QuestionGenerationRequest, QuestionGenerationResponse
from src.services.question_generation_service import get_question_generation_service
from src.core.logging import get_logger
from src.db.connection import DatabaseManager

router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    fastapi_request: Request,
    background_tasks: BackgroundTasks
) -> QuestionGenerationResponse:
    """
    Generate questions based on the provided parameters
    
    Args:
        request: Question generation request parameters
        fastapi_request: FastAPI request object
        background_tasks: Background tasks handler
        
    Returns:
        Question generation response
    """
    try:
        logger.info(f"Received question generation request: {request.dict()}")
        
        # Get source identifier (can be extended to include user info, etc.)
        source_id = f"api-{request.session_id}"
        
        # Get question generation service
        question_service = get_question_generation_service()
        
        # Generate questions
        response = await question_service.generate_questions(
            request=request,
            source_id=source_id
        )
        
        # Schedule background task to save to DynamoDB if available
        if hasattr(fastapi_request.app.state, 'db_manager'):
            db_manager: DatabaseManager = fastapi_request.app.state.db_manager
            if db_manager.history_table:
                background_tasks.add_task(
                    save_generation_history,
                    db_manager,
                    request,
                    response,
                    source_id
                )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{session_id}")
async def get_generation_status(
    session_id: str,
    fastapi_request: Request
) -> Dict[str, Any]:
    """
    Get the status of a question generation session
    
    Args:
        session_id: Session identifier
        fastapi_request: FastAPI request object
        
    Returns:
        Session status information
    """
    try:
        # Check if DB manager is available
        if not hasattr(fastapi_request.app.state, 'db_manager'):
            return {
                "session_id": session_id,
                "status": "unknown",
                "message": "Database not available"
            }
        
        db_manager: DatabaseManager = fastapi_request.app.state.db_manager
        
        # Check history table
        if db_manager.history_table:
            try:
                response = db_manager.history_table.get_item(
                    Key={'session_id': session_id}
                )
                
                if 'Item' in response:
                    item = response['Item']
                    return {
                        "session_id": session_id,
                        "status": item.get('status', 'unknown'),
                        "created_at": item.get('created_at', ''),
                        "completed_at": item.get('completed_at', ''),
                        "total_questions": item.get('total_questions', 0),
                        "files_generated": item.get('files_generated', [])
                    }
            except Exception as e:
                logger.warning(f"Error retrieving session status: {str(e)}")
        
        return {
            "session_id": session_id,
            "status": "not_found",
            "message": "Session not found"
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def save_generation_history(
    db_manager: DatabaseManager,
    request: QuestionGenerationRequest,
    response: QuestionGenerationResponse,
    source_id: str
) -> None:
    """
    Save question generation history to DynamoDB
    
    Args:
        db_manager: Database manager instance
        request: Original request
        response: Generation response
        source_id: Source identifier
    """
    try:
        if db_manager.history_table:
            from datetime import datetime
            
            item = {
                'session_id': request.session_id,
                'source_id': source_id,
                'created_at': datetime.utcnow().isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'status': response.status,
                'content_id': request.contentId,
                'chapter_name': request.chapter_name,
                'learning_objectives': request.learning_objectives,
                'total_questions': request.total_questions,
                'question_type_distribution': request.question_type_distribution,
                'difficulty_distribution': request.difficulty_distribution,
                'blooms_taxonomy_distribution': request.blooms_taxonomy_distribution,
                'files_generated': response.files_generated,
                'message': response.message
            }
            
            db_manager.history_table.put_item(Item=item)
            logger.info(f"Saved generation history for session: {request.session_id}")
            
    except Exception as e:
        logger.error(f"Error saving generation history: {str(e)}")