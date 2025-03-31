# app/routes.py
from flask import Blueprint, request, jsonify
from app.gemini_service import GeminiService
import json

# สร้าง blueprint
api = Blueprint('api', __name__)
gemini_service = GeminiService()

@api.route('/health', methods=['GET'])
def health_check():
    """API endpoint เพื่อตรวจสอบว่าระบบทำงานปกติ"""
    return jsonify({"status": "ok"})

@api.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint สำหรับถามคำถามแบบ RAG"""
    data = request.json
    
    if not data or 'question' not in data:
        return jsonify({"success": False, "error": "Missing question"}), 400
    
    question = data.get('question')
    temperature = data.get('temperature', 0.7)
    
    result = gemini_service.generate_with_rag(question, temperature)
    
    return jsonify(result), 200 if result["success"] else 500