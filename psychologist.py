#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass
from typing import List, Dict, Any

import gigachat
from gigachat import _models as giga_models

@dataclass
class DialogueConfig:
    ai_persona: str = "Ты эмпатичный помощник с психологическим образованием."
    conversation_temp: float = 0.72
    response_length: int = 95
    safety_margin: int = 5

class MentalSupportEngine:
    def __init__(self, auth_token: str):
        self._setup_connection(auth_token)
        self.dialogue_history = []
        self._initialize_ai_persona(DialogueConfig.ai_persona)
    
    def _setup_connection(self, token: str):
        """Configure secure connection with TLS verification disabled"""
        self.channel = gigachat.GigaChat(
            credentials=token,
            verify_ssl_certs=False,
            timeout=30
        )
    
    def _initialize_ai_persona(self, system_prompt: str):
        """Initialize conversation with system role message"""
        self.dialogue_history.append(
            giga_models.Messages(
                role=giga_models.MessagesRole.SYSTEM,
                content=system_prompt
            )
        )
    
    def process_user_input(self, human_input: str) -> str:
        """Process user message and generate AI response"""
        self._update_dialogue_history(human_input, is_user=True)
        
        conversation = giga_models.Chat(
            messages=self.dialogue_history,
            temperature=DialogueConfig.conversation_temp,
            max_tokens=DialogueConfig.response_length
        )
        
        with self.channel as ai_service:
            ai_response = ai_service.chat(conversation)
            bot_reply = self._extract_response_content(ai_response)
        
        self._update_dialogue_history(bot_reply, is_user=False)
        return bot_reply
    
    def _update_dialogue_history(self, text: str, is_user: bool):
        """Maintain conversation context"""
        message_type = giga_models.MessagesRole.USER if is_user else giga_models.MessagesRole.ASSISTANT
        self.dialogue_history.append(
            giga_models.Messages(role=message_type, content=text)
    
    def _extract_response_content(self, response) -> str:
        """Safely extract message content from response"""
        try:
            return response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            return f"Извините, произошла ошибка: {str(e)}"

def interactive_session(engine):
    """Run interactive conversation loop"""
    print("Сессия поддержки начата. Для выхода введите 'quit'")
    while True:
        try:
            user_text = input("> Ваше сообщение: ")
            if user_text.lower() in ('выход', 'quit', 'exit'):
                break
            
            response = engine.process_user_input(user_text)
            print("\nОтвет помощника:", response, "\n")
            
        except KeyboardInterrupt:
            print("\nСессия завершена.")
            break

if __name__ == "__main__":
    auth_token = os.getenv("GIGA_TOKEN") or "your_token_here"
    if not auth_token:
        raise ValueError("Необходимо указать токен авторизации")
    
    support_bot = MentalSupportEngine(auth_token)
    interactive_session(support_bot)