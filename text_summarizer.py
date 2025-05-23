from langchain_community.document_loaders import WikipediaLoader
from langchain_community.chat_models import GigaChat
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain

def fetch_wiki_content():
    """Загружает контент о петербургском метро из Википедии"""
    return WikipediaLoader(
        query="Петербургский метрополитен",
        lang="ru",
        load_max_docs=1,
        doc_content_chars_max=500000
    ).load()

def initialize_text_processor():
    """Инициализирует обработчик текста"""
    return RecursiveCharacterTextSplitter(
        chunk_size=12000,
        chunk_overlap=1500,
        separators=["\n\n", "\n", " ", ""]
    )

def create_custom_prompts():
    """Создаёт кастомные промпты для суммаризации"""
    map_template = """
    Проанализируйте текст и выделите ключевую информацию:
    {text}
    ОСНОВНЫЕ ПОЛОЖЕНИЯ:"""
    
    combine_template = """
    На основе предоставленных данных составьте краткий аналитический отчёт:
    {text}
    АНАЛИТИЧЕСКИЙ ОТЧЁТ:"""
    
    return {
        'map': PromptTemplate.from_template(map_template),
        'combine': PromptTemplate.from_template(combine_template)
    }

def setup_gigachat_model():
    """Настраивает модель GigaChat"""
    return GigaChat(
        credentials="your_credentials_here",
        scope="GIGACHAT_API_PERS",
        model="GigaChat-Pro",
        temperature=0.3,
        top_p=0.8,
        verify_ssl_certs=False
    )

def generate_summary(content, processor, prompts, llm):
    """Генерирует итоговое суммаризированное содержание"""
    processed_content = processor.split_documents(content)
    
    if len(processed_content) == 1:
        return load_summarize_chain(
            llm=llm,
            chain_type="stuff",
            prompt=prompts['combine']
        ).run(processed_content)
    else:
        return load_summarize_chain(
            llm=llm,
            chain_type="map_reduce",
            map_prompt=prompts['map'],
            combine_prompt=prompts['combine'],
            verbose=True
        ).run(processed_content)

def main():
    """Основной поток выполнения"""
    content_data = fetch_wiki_content()
    text_processor = initialize_text_processor()
    prompt_templates = create_custom_prompts()
    chat_model = setup_gigachat_model()
    
    result = generate_summary(content_data, text_processor, prompt_templates, chat_model)
    print("\nРЕЗУЛЬТАТ АНАЛИЗА ПЕТЕРБУРГСКОГО МЕТРО:")
    print(result)

if __name__ == "__main__":
    main()