"""
Engine Module for Nobile Career Protocol
Handles all OpenAI GPT integration and business logic
"""
from typing import Optional, Dict, List
from openai import OpenAI
import config
from prompts import PromptTemplates

class CareerEngine:
    """Main engine for career protocol GPT interactions"""
    
    def __init__(self):
        """Initialize the engine with OpenAI client"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found. Please set it in .env file")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        
    def _call_gpt(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generic GPT call handler
        
        Args:
            prompt: User prompt to send to GPT
            system_message: Optional system message for context
            
        Returns:
            GPT response text
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro ao processar solicitação: {str(e)}"
    
    def generate_diagnosis(self, position: str, salary: float) -> str:
        """
        Generate executive diagnosis
        
        Args:
            position: Current executive position
            salary: Current salary in BRL
            
        Returns:
            Diagnosis analysis from GPT
        """
        prompt = PromptTemplates.diagnosis_prompt(position, salary)
        system_message = "Você é um consultor executivo de carreira altamente experiente."
        return self._call_gpt(prompt, system_message)
    
    def calculate_ats_score(self, resume_text: str) -> Dict[str, any]:
        """
        Calculate ATS score for resume
        
        Args:
            resume_text: Extracted text from PDF resume
            
        Returns:
            Dictionary with score and analysis
        """
        prompt = PromptTemplates.ats_score_prompt(resume_text)
        system_message = "Você é um especialista em ATS (Applicant Tracking Systems)."
        response = self._call_gpt(prompt, system_message)
        
        # Parse response to extract score (basic implementation)
        # In production, you might want more sophisticated parsing
        return {
            "analysis": response,
            "raw_response": response
        }
    
    def conduct_metrics_interrogation(
        self, 
        position: str, 
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Conduct metrics interrogation session
        
        Args:
            position: Executive position
            context: Additional context
            conversation_history: Previous conversation for continuity
            
        Returns:
            Next question or analysis
        """
        if conversation_history:
            # Continue conversation with history
            messages = [
                {"role": "system", "content": "Você é um headhunter executivo experiente."}
            ]
            messages.extend(conversation_history)
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Erro ao processar: {str(e)}"
        else:
            # Start new interrogation
            prompt = PromptTemplates.metrics_interrogation_prompt(position, context)
            system_message = "Você é um headhunter executivo conduzindo entrevista de alto nível."
            return self._call_gpt(prompt, system_message)
    
    def extract_pdf_info(self, text: str) -> str:
        """
        Extract and structure information from PDF text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Structured information
        """
        prompt = PromptTemplates.pdf_extraction_prompt(text)
        system_message = "Você é um especialista em análise de currículos executivos."
        return self._call_gpt(prompt, system_message)
    
    def generate_career_strategy(
        self, 
        diagnosis: str, 
        ats_score: int, 
        metrics: str
    ) -> str:
        """
        Generate comprehensive career strategy
        
        Args:
            diagnosis: Diagnosis results
            ats_score: ATS score value
            metrics: Metrics interrogation insights
            
        Returns:
            Complete career strategy
        """
        prompt = PromptTemplates.career_strategy_prompt(diagnosis, ats_score, metrics)
        system_message = "Você é um consultor estratégico de carreira executiva."
        return self._call_gpt(prompt, system_message)
    
    def validate_executive_profile(self, position: str, salary: float) -> Dict[str, any]:
        """
        Validate if profile meets executive criteria
        
        Args:
            position: Current position
            salary: Current salary in BRL
            
        Returns:
            Validation result with status and message
        """
        is_valid = salary >= config.MIN_SALARY_REQUIREMENT
        
        return {
            "is_valid": is_valid,
            "position": position,
            "salary": salary,
            "min_requirement": config.MIN_SALARY_REQUIREMENT,
            "message": "Perfil validado para protocolo executivo." if is_valid 
                      else f"Salário abaixo do mínimo executivo (R$ {config.MIN_SALARY_REQUIREMENT:,.2f})"
        }
