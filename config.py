"""
Спільна конфігурація для всіх Kafka-скриптів ДЗ-5.
Імена топіків містять суфікс _zhuk_liudmyla, як і вимагає завдання.
"""
import os

# Bootstrap server — локальний broker з docker-compose.yml
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Особистий суфікс для унікальності імен топіків
NAME_SUFFIX = "_zhuk_liudmyla"

# Три топіки з завдання
TOPIC_SENSORS = f"building_sensors{NAME_SUFFIX}"
TOPIC_TEMPERATURE_ALERTS = f"temperature_alerts{NAME_SUFFIX}"
TOPIC_HUMIDITY_ALERTS = f"humidity_alerts{NAME_SUFFIX}"

# Пороги для сповіщень
TEMPERATURE_THRESHOLD = 40.0      # °C — якщо > 40, б'ємо на сполох
HUMIDITY_MIN = 20.0               # % — якщо < 20, сповіщення
HUMIDITY_MAX = 80.0               # % — якщо > 80, сповіщення

# Діапазон згенерованих показників
TEMPERATURE_RANGE = (25.0, 45.0)
HUMIDITY_RANGE = (15.0, 85.0)

# Частота генерації у producer.py (секунди між відправленнями)
PRODUCE_INTERVAL_SEC = 2.0
