from typing import Dict
from fastapi import HTTPException
from assistant.openai_assistant import ask_openai
from assistant.gemini_assistant import ask_gemini

async def agent_to_agent_communication(user_message: str) -> Dict:
    """
    Flow:
    1. User asks Gemini something
    2. Gemini formulates a question for ChatGPT
    3. ChatGPT answers that question
    4. Gemini processes ChatGPT's answer and responds to user
    """
    try:
        # 1. Gemini decides what to ask ChatGPT based on user's message
        gemini_question = await ask_gemini(
            f"Based on this user question: '{user_message}', "
            "formulate a detailed technical question for ChatGPT. "
            "Make the question specific and focused."
        )
        
        if not gemini_question:
            raise ValueError("Gemini failed to formulate a question for ChatGPT")
            
        # 2. Ask ChatGPT the question formulated by Gemini
        chatgpt_answer = await ask_openai(gemini_question)
        
        if not chatgpt_answer:
            raise ValueError("ChatGPT failed to provide an answer")
        
        # 3. Gemini processes ChatGPT's answer and provides final response to user
        final_response = await ask_gemini(
            f"I asked ChatGPT this question: '{gemini_question}' "
            f"And got this answer: '{chatgpt_answer}' "
            "Please analyze this answer and provide a clear, helpful response to the original user question. "
            "Make it conversational but informative."
        )
        
        if not final_response:
            raise ValueError("Gemini failed to process ChatGPT's answer")
        
        return {
            "status": "success",
            "final_response": final_response,
            "conversation_flow": {
                "original_user_question": user_message,
                "gemini_question_for_chatgpt": gemini_question,
                "chatgpt_answer": chatgpt_answer,
                "gemini_final_response": final_response
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in agent communication: {str(e)}"
        )






