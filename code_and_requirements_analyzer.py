import os
import logging
import time
import requests
import re
import html
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from langchain_gigachat.chat_models import GigaChat
from _config import TOKEN, credentials

# Инициализация GigaChat
gigachat_model = GigaChat(
    credentials=credentials,
    verify_ssl_certs=False,
    timeout=360,
    temperature=0.18,
    top_p=0.3,
    model="GigaChat-2-Max"
)

# Глобальные переменные
thread_id = random.randint(1, 1000)
config_ = {"configurable": {"thread_id": f'{thread_id}'}

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Состояния бота
class BotState(StatesGroup):
    active_session = State()

def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать анализ", callback_data="start_session")],
            [InlineKeyboardButton(text="🛑 Остановить", callback_data="stop_session")]
        ]
    )

def get_session_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛑 Завершить сессию", callback_data="stop_session")]
        ]
    )

@dp.message(Command("start"))
async def start_handler(message: Message):
    welcome_msg = """
🤖 <b>Добро пожаловать в анализатор требований и кода!</b>

Я могу помочь вам с:
✅ Анализом бизнес-требований
✅ Проверкой исходного кода
✅ Проверкой соответствия кода требованиям

Работаю с:
🔗 Ссылками на Confluence
📝 Прямым вводом текста

Для начала работы нажмите кнопку ниже 👇
    """
    await message.answer(welcome_msg, reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def help_handler(message: Message):
    help_msg = """
📚 <b>Справка по работе с ботом</b>

Мои возможности:
1. Анализ бизнес-требований:
   - Логические ошибки
   - Двусмысленные формулировки
   - Противоречия

2. Проверка соответствия кода требованиям

3. Анализ качества кода

4. Генерация отчетов

5. Сохранение результатов в Confluence

<b>Основные команды:</b>
/start - Начало работы
/stop - Завершить текущую сессию
/help - Эта справка

Для начала анализа просто отправьте:
- Текст требований и кода
- Или ссылки на Confluence
    """
    await message.answer(help_msg)

@dp.callback_query(lambda c: c.data == "start_session")
async def start_session(callback: CallbackQuery, state: FSMContext):
    init_msg = """
🔍 <b>Сессия анализа запущена!</b>

Теперь вы можете:
1. Отправить текст требований и кода
2. Прислать ссылки на Confluence
3. Задать вопрос по анализу

Пример запроса:
"Проанализируй эти требования: <текст>"
"Проверь соответствие этого кода требованиям: <код>"
    """
    await callback.message.answer(init_msg, reply_markup=get_session_keyboard())
    await state.set_state(BotState.active_session)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stop_session")
async def stop_session(callback: CallbackQuery, state: FSMContext):
    global config_
    thread_id = random.randint(1, 1000)
    config_ = {"configurable": {"thread_id": f'{thread_id}'}}
    
    await callback.message.answer("🛑 <b>Сессия завершена.</b> Данные очищены.\n\nДля нового анализа нажмите /start")
    await state.clear()
    await callback.answer()

@dp.message(BotState.active_session)
async def process_message(message: Message):
    try:
        user_text = message.text
        
        # Сначала получаем быстрый ответ от GigaChat
        quick_response = gigachat_model.invoke([
            SystemMessage(content="Дайте краткий ответ, что начали обработку запроса"),
            HumanMessage(content=user_text)
        ])
        
        await message.answer(f"🔎 <i>{quick_response.content}</i>")
        
        # Затем обрабатываем запрос через граф
        full_response = graph.invoke({"messages": user_text}, config=config_)
        response_content = full_response["messages"][-1].content
        
        # Если ответ слишком длинный, отправляем файлом
        if len(response_content) > 4000:
            with open('response.txt', 'w', encoding="utf-8") as f:
                f.write(response_content)
            await message.answer_document(
                document=FSInputFile('response.txt'),
                caption="📄 Вот результаты анализа:"
            )
        else:
            await message.answer(f"📋 <b>Результаты анализа:</b>\n\n{response_content}")
            
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        await message.answer("⚠️ Произошла ошибка при обработке запроса. Попробуйте снова или завершите сессию /stop")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())