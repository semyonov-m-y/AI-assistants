# Импорт необходимых библиотек
import getpass
import os
from gigachat import GigaChat
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Настройка аутентификации
def setup_credentials():
    """Настройка учетных данных для GigaChat"""
    if "GIGACHAT_CREDENTIALS" not in os.environ:
        os.environ["GIGACHAT_CREDENTIALS"] = getpass.getpass("Введите учетные данные GigaChat: ")

# Инициализация анализатора изображений
class ImageAnalyzer:
    def __init__(self):
        """Инициализация клиента GigaChat"""
        self.client = GigaChat(
            base_url="https://gigachat-preview.devices.sberbank.ru/api/v1",
            verify_ssl_certs=False,
            timeout=600,
            model="GigaChat-Pro-preview",
        )
    
    def load_image(self, image_path):
        """Загрузка и отображение изображения"""
        try:
            img = Image.open(image_path)
            plt.figure(figsize=(10, 6))
            plt.imshow(img)
            plt.axis('off')
            plt.title("Анализируемое изображение")
            plt.show()
            return np.array(img)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return None
    
    def analyze_image(self, image_array, analysis_type="general"):
        """Анализ изображения с разными вариантами запросов"""
        analysis_tasks = {
            "general": "Опишите содержание этого изображения максимально подробно",
            "objects": "Перечислите все основные объекты на изображении",
            "context": "Проанализируйте контекст и возможное значение изображения",
            "details": "Опишите детали изображения: цвета, композицию, стиль"
        }
        
        task = analysis_tasks.get(analysis_type, analysis_tasks["general"])
        
        try:
            response = self.client.analyze_image(
                image=image_array,
                task=task
            )
            return response
        except Exception as e:
            print(f"Ошибка анализа изображения: {e}")
            return None
    
    def print_analysis_results(self, results):
        """Красивый вывод результатов анализа"""
        if not results:
            print("Не удалось получить результаты анализа")
            return
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА ИЗОБРАЖЕНИЯ".center(50))
        print("="*50)
        
        for key, value in results.items():
            print(f"\n{key.upper()}:")
            print("-"*30)
            if isinstance(value, list):
                for item in value:
                    print(f"• {item}")
            else:
                print(value)
        
        print("\n" + "="*50)

# Основная функция
def main():
    print("\n" + "="*50)
    print("УНИВЕРСАЛЬНЫЙ АНАЛИЗАТОР ИЗОБРАЖЕНИЙ".center(50))
    print("="*50 + "\n")
    
    # Настройка учетных данных
    setup_credentials()
    
    # Инициализация анализатора
    analyzer = ImageAnalyzer()
    
    # Выбор типа анализа
    analysis_types = {
        "1": "general",
        "2": "objects",
        "3": "context",
        "4": "details"
    }
    
    print("Выберите тип анализа:")
    for num, desc in analysis_types.items():
        print(f"{num}. {desc.capitalize()}")
    
    choice = input("\nВаш выбор (1-4): ")
    analysis_type = analysis_types.get(choice, "general")
    
    # Загрузка изображения
    image_path = input("\nВведите путь к изображению: ")
    image_array = analyzer.load_image(image_path)
    
    if image_array is not None:
        # Анализ изображения
        results = analyzer.analyze_image(image_array, analysis_type)
        
        # Вывод результатов
        analyzer.print_analysis_results(results)

if __name__ == "__main__":
    main()