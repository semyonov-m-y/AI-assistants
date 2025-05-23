"""Пример - использование функций с Google Search"""

import json
from googlesearch import search as google_search

from gigachat.models import Chat, Function, FunctionParameters, Messages, MessagesRole
from gigachat import GigaChat

def search_google(search_query, num_results=3):
    """Поиск в Google. Возвращает первые N результатов."""
    try:
        return "\n".join([result for result in google_search(search_query, num_results=num_results, lang="ru")])
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

# Используйте токен, полученный в личном кабинете из поля Авторизационные данные
with GigaChat(
    credentials=...,
    model=... # Model with functions
) as giga:
    search = Function(
        name="google_search",
        description="""Поиск в Google.
Полезен, когда нужно ответить на вопросы о текущих событиях.
Входными данными должен быть поисковый запрос.""",
        parameters=FunctionParameters(
            type="object",
            properties={"query": {"type": "string", "description": "Поисковый запрос"}},
            required=["query"],
        ),
    )

    messages = []
    function_called = False
    while True:
        if not function_called:
            query = input("\033[92mUser: \033[0m")
            messages.append(Messages(role=MessagesRole.USER, content=query))

        chat = Chat(messages=messages, functions=[search])

        resp = giga.chat(chat).choices[0]
        mess = resp.message
        messages.append(mess)

        print("\033[93m" + f"Bot: \033[0m{mess.content}")

        function_called = False
        func_result = ""
        if resp.finish_reason == "function_call":
            print("\033[90m" + f"  >> Processing function call {mess.function_call}" + "\033[0m")
            if mess.function_call.name == "google_search":
                query = mess.function_call.arguments.get("query", None)
                if query:
                    func_result = search_google(query)
            print("\033[90m" + f"  << Function result: {func_result}\n\n" + "\033[0m")

            messages.append(
                Messages(role=MessagesRole.FUNCTION,
                         content=json.dumps({"result": func_result}, ensure_ascii=False))
            )
            function_called = True