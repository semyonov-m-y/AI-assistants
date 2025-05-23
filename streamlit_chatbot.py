import streamlit as st
from langchain_community.chat_models import GigaChat
from langchain.schema import ChatMessage

# Настройка заголовка приложения
st.title("Чат-бот на GigaChat")

# Боковая панель с настройками подключения
with st.sidebar:
    st.header("Настройки подключения")
    
    # Выбор модели
    model = st.selectbox(
        "Модель GigaChat",
        (
            "GigaChat",
            "GigaChat-Pro",
            "GigaChat-Plus",
        ),
        index=0
    )
    
    # Выбор API endpoint
    base_url = st.selectbox(
        "API сервер",
        (
            "https://gigachat.devices.sberbank.ru/api/v1",
            "https://beta.saluteai.sberdevices.ru/v1",
        ),
        index=0
    )
    
    st.header("Авторизация")
    
    # Варианты авторизации
    auth_method = st.radio(
        "Способ авторизации",
        ("По credentials", "По токену", "По логину/паролю")
    )
    
    if auth_method == "По credentials":
        credentials = st.text_input("Ваши credentials", type="password")
    elif auth_method == "По токену":
        access_token = st.text_input("Access token", type="password")
    else:
        user = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")

# Инициализация истории сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        ChatMessage(
            role="system",
            content="Вы общаетесь с ИИ-ассистентом на основе GigaChat. Задавайте вопросы.",
        ),
        ChatMessage(
            role="assistant",
            content="Здравствуйте! Я ваш ИИ-помощник. Чем могу помочь?",
            additional_kwargs={"render_content": "Здравствуйте! Я ваш ИИ-помощник. Чем могу помочь?"},
        ),
    ]

# Отображение истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message.role):
        if message.role == "assistant":
            st.markdown(message.additional_kwargs["render_content"], True)
        else:
            st.markdown(message.content, True)

# Обработка ввода пользователя
if user_input := st.chat_input("Введите ваше сообщение..."):
    # Проверка авторизации
    if not any([locals().get('access_token'), locals().get('credentials'), (locals().get('user') and locals().get('password'))]):
        st.warning("Для работы чата необходимо указать данные авторизации")
        st.stop()

    # Инициализация модели GigaChat
    chat = GigaChat(
        base_url=base_url,
        credentials=credentials if auth_method == "По credentials" else None,
        model=model,
        access_token=st.session_state.get("token") or locals().get('access_token'),
        user=user if auth_method == "По логину/паролю" else None,
        password=password if auth_method == "По логину/паролю" else None,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
    ).bind_tools(tools=[], tool_choice="auto")

    # Добавление сообщения пользователя в историю
    user_message = ChatMessage(role="user", content=user_input)
    st.session_state.messages.append(user_message)

    # Отображение сообщения пользователя
    with st.chat_message(user_message.role):
        st.markdown(user_message.content)

    # Подготовка сообщения ассистента
    assistant_message = ChatMessage(
        role="assistant", 
        content="", 
        additional_kwargs={"render_content": ""}
    )
    st.session_state.messages.append(assistant_message)

    # Генерация и потоковый вывод ответа
    with st.chat_message(assistant_message.role):
        message_area = st.empty()
        loading_indicator = None
        
        for response_chunk in chat.stream(st.session_state.messages):
            if response_chunk.type == "FunctionInProgressMessage":
                if not loading_indicator:
                    loading_indicator = st.spinner(text="Обработка...")
                    loading_indicator.__enter__()
                continue
            else:
                if loading_indicator:
                    loading_indicator.__exit__(None, None, None)
                    loading_indicator = None
                
                # Обработка контента
                if response_chunk.additional_kwargs.get("image_uuid"):
                    image_data = chat.get_file(response_chunk.additional_kwargs["image_uuid"]).content
                    assistant_message.additional_kwargs["render_content"] += f"""<img src="data:png;base64,{image_data}" style="width: 450px; display: block; border-radius: 10px;">"""
                else:
                    assistant_message.additional_kwargs["render_content"] += response_chunk.content
                
                assistant_message.content += response_chunk.content
                assistant_message.additional_kwargs = {
                    **assistant_message.additional_kwargs,
                    **response_chunk.additional_kwargs,
                }

                message_area.markdown(
                    assistant_message.additional_kwargs["render_content"] + "▌", 
                    True
                )
        
        message_area.markdown(assistant_message.additional_kwargs["render_content"], True)

    # Сохранение токена для последующих запросов
    st.session_state.token = chat._client.token
    chat._client.close()