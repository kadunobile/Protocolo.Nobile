"""
Motor de lógica de IA e integração com OpenAI para o Nobile Career Strategy
"""

import openai
import json
import streamlit as st
from config import MAX_CV_TEXT_LENGTH, MAX_CV_TEXT_LENGTH_ATS


def get_response(messages, api_key):
    """
    Obtém resposta do modelo GPT-4o
    
    Args:
        messages: Lista de mensagens no formato OpenAI
        api_key: Chave API da OpenAI
        
    Returns:
        str: Resposta do modelo ou mensagem de erro
    """
    if not api_key:
        return "⚠️ Insira a API Key na barra lateral."
    
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"


def extract_role_from_cv(cv_text, api_key):
    """
    Extrai o cargo/função principal do CV usando IA
    
    Args:
        cv_text: Texto completo do CV
        api_key: Chave API da OpenAI
        
    Returns:
        str: Nome do cargo/função identificado ou "Profissional" como padrão
    """
    if not api_key:
        return "Cargo não identificado"
    
    client = openai.OpenAI(api_key=api_key)

    prompt = f"""
    Analise este CV e identifique o cargo/função principal da pessoa.

    CV: {cv_text[:MAX_CV_TEXT_LENGTH]}

    Retorne APENAS o nome do cargo/função (ex: "Gerente de Vendas", "Desenvolvedor Python", "Diretor Comercial").
    Seja específico e conciso (máximo 4 palavras).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        role = response.choices[0].message.content.strip()
        return role if role else "Profissional"
    except Exception as e:
        return "Profissional"


def calculate_ats_score(cv_text, target_role, api_key):
    """
    Calcula o Score ATS e identifica keywords faltantes
    
    Args:
        cv_text: Texto completo do CV
        target_role: Cargo alvo para análise
        api_key: Chave API da OpenAI
        
    Returns:
        dict: Dicionário com ats_score, keywords_present, keywords_missing, recomendacoes
              ou None em caso de erro
    """
    if not api_key:
        return None
    
    client = openai.OpenAI(api_key=api_key)

    prompt = f"""
    ATUE COMO: Auditor de RH e Especialista em ATS.
    CONTEXTO:
    - CV Texto: {cv_text[:MAX_CV_TEXT_LENGTH_ATS]}
    - Cargo Alvo: {target_role}

    TAREFA (Retorne JSON):
    1. **ATS_Score**: Calcule a % de palavras-chave do cargo presentes no CV (0-100).
    2. **Keywords_Present**: Liste 5-10 palavras-chave PRESENTES no CV.
    3. **Keywords_Missing**: Liste 5-10 palavras-chave críticas que FALTAM.
    4. **Recomendacoes**: Liste 3 recomendações curtas para melhorar o score.

    FORMATO JSON OBRIGATÓRIO:
    {{
        "ats_score": 0,
        "keywords_present": ["k1", "k2", "k3"],
        "keywords_missing": ["k1", "k2", "k3"],
        "recomendacoes": ["r1", "r2", "r3"]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Erro no cálculo ATS: {e}")
        return None
