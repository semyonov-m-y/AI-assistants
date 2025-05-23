import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import uuid

# Инициализация окружения
load_dotenv()

class ImageCreator:
    def __init__(self):
        self.api_url = "https://gigachat.dev/api/v1"
        self.session = requests.Session()
        self.session.verify = False
        self.timeout = 600
        self.model_name = "GigaPet"
        
        # Получаем ключ API из переменных окружения
        self.api_key = os.getenv("GIGA_API_SECRET")
        if not self.api_key:
            raise ValueError("API ключ не найден в .env файле")
            
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def generate_from_text(self, prompt_text):
        """Создает изображение на основе текстового описания"""
        try:
            # Формируем запрос для генерации изображения
            request_data = {
                "model": self.model_name,
                "messages": [{
                    "role": "user",
                    "content": prompt_text
                }],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            # Отправляем запрос к API
            response = self.session.post(
                f"{self.api_url}/images/generate",
                json=request_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Получаем данные изображения
            image_data = response.json()
            if not image_data.get("success", False):
                raise ValueError("Ошибка генерации изображения")
                
            return image_data["image_url"]
            
        except Exception as e:
            print(f"Ошибка при генерации изображения: {str(e)}")
            return None

    def save_image(self, image_url, filename=None):
        """Сохраняет изображение по URL на диск"""
        if not filename:
            # Генерируем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    
            print(f"Изображение сохранено как: {filename}")
            return filename
            
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {str(e)}")
            return None

# Пример использования
if __name__ == "__main__":
    try:
        # Создаем экземпляр генератора изображений
        artist = ImageCreator()
        
        # Запрашиваем изображение собаки
        dog_prompt = "Создай реалистичное изображение золотистого ретривера, играющего в парке"
        image_url = artist.generate_from_text(dog_prompt)
        
        if image_url:
            # Сохраняем изображение
            artist.save_image(image_url, "happy_golden_retriever.jpg")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")