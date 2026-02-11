"""
Configuration module for Nobile Career Protocol
Contains all application constants and settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"

# Application Constants
MIN_SALARY_REQUIREMENT = 20000  # R$ 20k+
APP_TITLE = "Nobile Career Protocol"
APP_ICON = "🎯"

# Sidebar Commands
SIDEBAR_COMMANDS = {
    "upload_pdf": "📄 Upload PDF",
    "diagnosis": "🔍 Diagnóstico Executivo",
    "ats_score": "📊 Score ATS",
    "metrics_interrogation": "💼 Interrogatório de Métricas"
}

# Session State Keys
SESSION_KEYS = {
    "pdf_uploaded": "pdf_uploaded",
    "diagnosis_complete": "diagnosis_complete",
    "current_position": "current_position",
    "current_salary": "current_salary",
    "ats_score": "ats_score",
    "pdf_content": "pdf_content",
    "conversation_history": "conversation_history"
}
