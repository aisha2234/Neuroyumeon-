# server.py
from fastapi import FastAPI
import requests
from pydantic import BaseModel
import openai  # pip install openai
import os

app = FastAPI()

# Настройки OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Добавь свой ключ OpenAI

# Модель входных данных
class CityData(BaseModel):
    traffic: dict  # {'улица1': congestion%, ...}
    emergency: dict  # {'служба1': available_units, ...}
    weather_city: str

# Функция получения погоды через Open Meteo
def get_weather(city):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
    )
    if response.status_code == 200:
        return response.json()['current_weather']
    return {"temp": None, "weathercode": None}

# Фильтр критических кейсов
def filter_critical(data):
    critical_cases = []
    # Транспорт
    for street, congestion in data['traffic'].items():
        if congestion > 80:  # критическая пробка
            critical_cases.append(f"Транспорт: {street} загружен на {congestion}%")
    # Экстренные службы
    for service, units in data['emergency'].items():
        if units < 2:  # критический недостаток
            critical_cases.append(f"Служба {service} имеет всего {units} единиц доступных")
    return critical_cases

# Генерация executive summary через LLM
def generate_summary(critical_cases, weather):
    prompt = f"""
Ты советник Акима. Ниже приведены критические события в городе и текущая погода:
Критические события: {critical_cases}
Погода: {weather}
Составь краткий executive summary (5–7 строк), выделяя только самые важные кейсы и рекомендации.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response['choices'][0]['message']['content']

# API endpoint
@app.post("/city-summary")
def city_summary(city_data: CityData):
    weather = get_weather({"lat": 43.238949, "lon": 76.889709})  # пример для Алматы
    critical_cases = filter_critical(city_data.dict())
    summary = generate_summary(critical_cases, weather)
    return {"executive_summary": summary, "critical_cases": critical_cases, "weather": weather}
