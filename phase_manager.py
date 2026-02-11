"""
Phase Manager for Nobile Career Strategy - FSM-based phase control
"""

from enum import Enum
import logging

# Get logger without configuring at module level
logger = logging.getLogger(__name__)

# Import FSM constants from config
try:
    from config import (
        FSM_MIN_MESSAGE_PAIRS_FOR_MENU,
        FSM_MIN_AI_MESSAGES_FOR_DIAGNOSTICO_EM_ANDAMENTO,
        FSM_TRIGGER_KEYWORDS,
        FSM_COMMAND_KEYWORDS
    )
except ImportError:
    # Fallback to defaults if config is not available
    FSM_MIN_MESSAGE_PAIRS_FOR_MENU = 4
    FSM_MIN_AI_MESSAGES_FOR_DIAGNOSTICO_EM_ANDAMENTO = 1
    FSM_TRIGGER_KEYWORDS = ["O USUÁRIO SUBIU", "ACIONOU"]
    FSM_COMMAND_KEYWORDS = ["ACIONOU", "/otimizador_cv_linkedin", "ETAPA 5: ARQUIVO MESTRE"]


class Phase(Enum):
    """
    Enum representing the different phases of the application
    """
    UPLOAD = "UPLOAD"
    DIAGNOSTICO = "DIAGNOSTICO"
    DIAGNOSTICO_EM_ANDAMENTO = "DIAGNOSTICO_EM_ANDAMENTO"
    MENU = "MENU"
    EXECUCAO = "EXECUCAO"


class PhaseManager:
    """
    Manages phase transitions using a Finite State Machine (FSM) approach.
    Uses message counting instead of fragile keyword matching.
    """
    
    def __init__(self):
        """Initialize the phase manager with UPLOAD phase"""
        self.current_phase = Phase.UPLOAD
        self.cv_loaded = False
        
    def get_phase_value(self) -> str:
        """
        Get the string value of the current phase for compatibility with session_state
        
        Returns:
            str: Current phase value
        """
        return self.current_phase.value
    
    def count_user_ai_pairs(self, messages: list) -> int:
        """
        Count user-AI message pairs, excluding system messages and internal triggers
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            int: Number of user-AI pairs
        """
        count = 0
        for msg in messages:
            # Skip system messages and internal triggers
            if msg.get("role") == "system":
                continue
            content = str(msg.get("content", "")).upper()  # Case-insensitive matching
            # Use trigger keywords from config (case-insensitive)
            if any(keyword.upper() in content for keyword in FSM_TRIGGER_KEYWORDS):
                continue
            if msg.get("role") in ["user", "assistant"]:
                count += 1
        # Return pairs (divide by 2 since we count both user and assistant messages)
        return count // 2
    
    def transition_to_diagnostico(self, cv_content: str) -> bool:
        """
        Transition from UPLOAD to DIAGNOSTICO when CV is loaded
        
        Args:
            cv_content: CV text content
            
        Returns:
            bool: True if transition occurred
        """
        if self.current_phase == Phase.UPLOAD and cv_content:
            self.current_phase = Phase.DIAGNOSTICO
            self.cv_loaded = True
            logger.info("Phase transition: UPLOAD → DIAGNOSTICO (CV loaded)")
            return True
        return False
    
    def transition_to_diagnostico_em_andamento(self, messages: list) -> bool:
        """
        Transition from DIAGNOSTICO to DIAGNOSTICO_EM_ANDAMENTO after AI responds
        
        Args:
            messages: List of all messages
            
        Returns:
            bool: True if transition occurred
        """
        if self.current_phase == Phase.DIAGNOSTICO and messages:
            # Count AI messages after the diagnostic phase started
            ai_count = 0
            for msg in messages:
                if msg.get("role") == "assistant":
                    ai_count += 1
            
            # Use threshold from config
            if ai_count >= FSM_MIN_AI_MESSAGES_FOR_DIAGNOSTICO_EM_ANDAMENTO:
                self.current_phase = Phase.DIAGNOSTICO_EM_ANDAMENTO
                logger.info("Phase transition: DIAGNOSTICO → DIAGNOSTICO_EM_ANDAMENTO (≥1 AI message)")
                return True
        return False
    
    def transition_to_menu(self, messages: list) -> bool:
        """
        Transition from DIAGNOSTICO_EM_ANDAMENTO to MENU after sufficient interaction
        
        Args:
            messages: List of all messages
            
        Returns:
            bool: True if transition occurred
        """
        if self.current_phase == Phase.DIAGNOSTICO_EM_ANDAMENTO and messages:
            pairs = self.count_user_ai_pairs(messages)
            
            # Use threshold from config
            if pairs >= FSM_MIN_MESSAGE_PAIRS_FOR_MENU:
                self.current_phase = Phase.MENU
                logger.info(f"Phase transition: DIAGNOSTICO_EM_ANDAMENTO → MENU ({pairs} message pairs)")
                return True
        return False
    
    def transition_to_execucao(self, last_message_content: str) -> bool:
        """
        Transition from MENU to EXECUCAO when a command is triggered
        
        Args:
            last_message_content: Content of the last message
            
        Returns:
            bool: True if transition occurred
        """
        if self.current_phase == Phase.MENU:
            # Use command keywords from config (case-insensitive matching)
            content_upper = last_message_content.upper()
            if any(keyword.upper() in content_upper for keyword in FSM_COMMAND_KEYWORDS):
                self.current_phase = Phase.EXECUCAO
                logger.info("Phase transition: MENU → EXECUCAO (command triggered)")
                return True
        return False
    
    def update_phase(self, cv_content: str = None, messages: list = None) -> str:
        """
        Update the phase based on current state and inputs.
        This is the main method to call for automatic phase management.
        
        Args:
            cv_content: CV text content (optional)
            messages: List of all messages (optional)
            
        Returns:
            str: Current phase value after update
        """
        if cv_content and not self.cv_loaded:
            self.transition_to_diagnostico(cv_content)
        
        if messages:
            # Try transitions in logical order
            if self.current_phase == Phase.DIAGNOSTICO:
                self.transition_to_diagnostico_em_andamento(messages)
            
            elif self.current_phase == Phase.DIAGNOSTICO_EM_ANDAMENTO:
                self.transition_to_menu(messages)
            
            elif self.current_phase == Phase.MENU and len(messages) > 0:
                # Check if last message (from button click) contains a command trigger
                # Note: This is primarily called explicitly from app.py when buttons are clicked
                last_msg = messages[-1]
                if last_msg.get("role") == "user":  # Only check user messages
                    self.transition_to_execucao(str(last_msg.get("content", "")))
        
        return self.get_phase_value()
    
    def reset(self):
        """Reset the phase manager to initial state"""
        self.current_phase = Phase.UPLOAD
        self.cv_loaded = False
        logger.info("Phase manager reset to UPLOAD")
