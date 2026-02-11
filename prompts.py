"""
Prompts Module for Nobile Career Protocol
Centralized repository for all GPT prompt templates
"""

class PromptTemplates:
    """Centralized prompt templates for all application features"""
    
    @staticmethod
    def diagnosis_prompt(position: str, salary: float) -> str:
        """
        Generate diagnosis prompt for executive profile
        
        Args:
            position: Current executive position
            salary: Current salary in BRL
            
        Returns:
            Formatted prompt for GPT diagnosis
        """
        return f"""
Você é um consultor executivo especializado em carreiras de alto nível.

Analise o perfil executivo:
- Cargo: {position}
- Salário: R$ {salary:,.2f}

Forneça um diagnóstico detalhado sobre:
1. Posicionamento no mercado
2. Potencial de crescimento
3. Áreas de desenvolvimento prioritárias
4. Estratégias de avanço de carreira

Seja direto e estratégico na análise.
"""
    
    @staticmethod
    def ats_score_prompt(resume_text: str) -> str:
        """
        Generate ATS score calculation prompt
        
        Args:
            resume_text: Extracted text from PDF resume
            
        Returns:
            Formatted prompt for ATS score analysis
        """
        return f"""
Você é um especialista em sistemas ATS (Applicant Tracking Systems).

Analise o currículo a seguir e calcule um Score ATS de 0 a 100:

{resume_text}

Avalie:
1. Palavras-chave relevantes
2. Formatação e estrutura
3. Clareza de conquistas e resultados
4. Uso de verbos de ação
5. Quantificação de resultados

Forneça:
- Score ATS (0-100)
- Pontos fortes
- Pontos de melhoria
- Recomendações específicas
"""
    
    @staticmethod
    def metrics_interrogation_prompt(position: str, context: str) -> str:
        """
        Generate metrics interrogation prompt
        
        Args:
            position: Executive position
            context: Additional context from conversation
            
        Returns:
            Formatted prompt for metrics interrogation
        """
        return f"""
Você é um headhunter executivo conduzindo uma entrevista de alto nível.

Cargo em análise: {position}
Contexto: {context}

Conduza um "interrogatório de métricas" profundo:
1. Faça perguntas específicas sobre KPIs e resultados quantificáveis
2. Explore impacto no negócio e resultados financeiros
3. Investigue cases de sucesso com números concretos
4. Questione sobre metodologias de gestão e liderança

Faça uma pergunta de cada vez, de forma direta e incisiva.
Aguarde a resposta antes de prosseguir para a próxima pergunta.
"""
    
    @staticmethod
    def pdf_extraction_prompt(text: str) -> str:
        """
        Generate prompt for PDF content extraction and structuring
        
        Args:
            text: Raw text extracted from PDF
            
        Returns:
            Formatted prompt for content structuring
        """
        return f"""
Extraia e estruture as informações principais deste currículo:

{text}

Identifique e organize:
1. Dados pessoais (nome, contato)
2. Cargo atual e histórico profissional
3. Formação acadêmica
4. Competências principais
5. Principais realizações e resultados

Apresente de forma estruturada e clara.
"""
    
    @staticmethod
    def career_strategy_prompt(diagnosis: str, ats_score: int, metrics: str) -> str:
        """
        Generate comprehensive career strategy prompt
        
        Args:
            diagnosis: Executive diagnosis results
            ats_score: ATS score value
            metrics: Metrics interrogation insights
            
        Returns:
            Formatted prompt for career strategy development
        """
        return f"""
Você é um consultor de carreira executiva criando uma estratégia personalizada.

Dados disponíveis:
- Diagnóstico: {diagnosis}
- Score ATS: {ats_score}/100
- Insights de Métricas: {metrics}

Desenvolva uma estratégia de carreira executiva completa:
1. Objetivos de curto, médio e longo prazo
2. Ações imediatas para fortalecimento do perfil
3. Posicionamento no mercado e networking
4. Desenvolvimento de competências críticas
5. Plano de ação com timeline

Seja específico e orientado a resultados.
"""

# Additional prompt placeholders for future expansion
class PromptModifiers:
    """Modifiers and variations for prompts"""
    
    TONE_DIRECT = "Seja direto e objetivo."
    TONE_DETAILED = "Forneça análise detalhada e aprofundada."
    TONE_STRATEGIC = "Foque em aspectos estratégicos e de alto impacto."
    
    FORMAT_BULLET = "Apresente em formato de bullet points."
    FORMAT_PARAGRAPH = "Apresente em parágrafos bem estruturados."
    FORMAT_TABLE = "Apresente em formato de tabela quando aplicável."
