#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import time
from dataclasses import dataclass
from typing import List

@dataclass
class ChatMessage:
    actor: str  # 'system', 'bot' или 'user'
    text: str

class AIStreamHandler:
    def __init__(self):
        from gigachat import GigaChat as AIClient
        from gigachat.models import Chat as AIConversation
        from gigachat.models import Messages as AIMessage
        from gigachat.models import MessagesRole as AIRole
        
        self._AIClient = AIClient
        self._AIConversation = AIConversation
        self._AIMessage = AIMessage
        self._AIRole = AIRole
        
        self.chat_history = self._init_chat_history()

    def _init_chat_history(self):
        """Инициализирует историю сообщений"""
        return self._AIConversation(
            messages=[
                self._AIMessage(
                    role=self._AIRole.SYSTEM,
                    content="Ты - компетентный цифровой ассистент."
                ),
                self._AIMessage(
                    role=self._AIRole.ASSISTANT,
                    content="Чем могу быть полезен?"
                ),
                self._AIMessage(
                    role=self._AIRole.USER,
                    content="Составь развёрнутый доклад о московском периоде жизни Пушкина"
                )
            ]
        )

    async def process_stream(self):
        """Обрабатывает потоковый вывод"""
        async with self._AIClient() as ai:
            async for response in ai.astream(self.chat_history):
                print(f"{time.time():.6f} | {response}", flush=True)

async def execute():
    handler = AIStreamHandler()
    await handler.process_stream()

if __name__ == "__main__":
    try:
        asyncio.run(execute())
    except KeyboardInterrupt:
        print("\nСеанс завершён")