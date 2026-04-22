# goit-de-hw-05

Домашнє завдання 5 з курсу Data Engineering (GoIT Neoversity).
Тема: **Apache Kafka** — IoT-система моніторингу температури й вологості.

Три топіки з суфіксом `_zhuk_liudmyla`:

- `building_sensors_zhuk_liudmyla` — сирі дані з датчиків;
- `temperature_alerts_zhuk_liudmyla` — сповіщення про перевищення температури > 40 °C;
- `humidity_alerts_zhuk_liudmyla` — сповіщення, якщо вологість < 20 % або > 80 %.

## Структура проєкту

```
goit-de-hw-05/
├── docker-compose.yml       # Kafka (bitnami, KRaft mode, без Zookeeper)
├── config.py                # Константи: bootstrap, імена топіків, пороги
├── create_topics.py         # Крок 1: створює 3 топіки
├── producer.py              # Крок 2: імітує датчик, пише в building_sensors
├── processor.py             # Крок 3: читає building_sensors, шле alert'и
├── alert_consumer.py        # Крок 4: слухає обидва alert-топіки, друкує
├── requirements.txt         # kafka-python
├── run.sh                   # Хелпер: setup / topics / producer / proc / alerts / down
├── screenshots/             # Скриншоти виконання за кожен крок
└── README.md
```

## Передумови

- **Docker Desktop** запущений (для локального Kafka).
- **Python 3.9+**.

## Крок за кроком

### 0. Старт Kafka + створення топіків

```bash
bash run.sh setup
```

Команда:
1. Піднімає Kafka-контейнер (KRaft mode, без Zookeeper).
2. Створює venv, ставить `kafka-python`.
3. Виконує `create_topics.py`, який робить топіки й друкує список існуючих:

```python
[print(topic) for topic in admin_client.list_topics() if "_zhuk_liudmyla" in topic]
```

Очікуваний вивід — усі три топіки з суфіксом `_zhuk_liudmyla`.

### 1. Запуск датчиків

Відкрийте два (чи більше) термінали й у кожному виконайте:

```bash
bash run.sh producer
```

Кожен запуск = окремий датчик із випадковим `sensor_id`, що залишається незмінним до Ctrl+C. Повідомлення відправляються раз на `PRODUCE_INTERVAL_SEC` секунд (2 с за замовчуванням).

### 2. Фільтрація та надсилання сповіщень

У ще одному терміналі:

```bash
bash run.sh proc
```

Скрипт слухає `building_sensors_zhuk_liudmyla`, і якщо температура > 40 °C або вологість поза [20;80] — створює сповіщення й пише у відповідний alert-топік.

### 3. Споживач сповіщень

В окремому терміналі:

```bash
bash run.sh alerts
```

Підписується на `temperature_alerts_zhuk_liudmyla` і `humidity_alerts_zhuk_liudmyla`, виводить кожне отримане сповіщення.

### Зупинка

```bash
bash run.sh down
```

## Формат повідомлень

Повідомлення у `building_sensors`:
```json
{
  "sensor_id": "sensor-a1b2c3d4",
  "timestamp": "2026-04-22T09:12:34Z",
  "temperature": 37.45,
  "humidity": 68.12
}
```

Повідомлення в alert-топіках:
```json
{
  "sensor_id": "sensor-a1b2c3d4",
  "timestamp": "2026-04-22T09:12:36Z",
  "alert_generated_at": "2026-04-22T09:12:36Z",
  "metric": "temperature",
  "value": 42.81,
  "message": "Temperature 42.81°C exceeds threshold 40.0°C"
}
```

## Скриншоти

У теці `screenshots/` містяться:

- `p1_topics.png` — вивід `create_topics.py`: три топіки з суфіксом `_zhuk_liudmyla`.
- `p2_producers.png` — два запущених датчики (в двох терміналах одночасно).
- `p3_processor.png` — processor читає з `building_sensors` та відфільтровує.
- `p4_alerts_in_topics.png` — відфільтровані дані потрапили в `temperature_alerts` / `humidity_alerts` (видно у processor логах або через `kafka-console-consumer`).
- `p5_alert_consumer.png` — фінальний consumer виводить сповіщення.
