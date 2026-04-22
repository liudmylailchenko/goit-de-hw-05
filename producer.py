"""
Крок 2. Імітує один датчик, що періодично відправляє температуру та вологість
у топік building_sensors_zhuk_liudmyla.

Один запуск = один датчик (ID згенерованo випадково та незмінний для цього запуску).
Щоб імітувати кілька датчиків — запустіть скрипт у декількох терміналах.

Використання:  python producer.py
"""
import json
import random
import time
import uuid
from datetime import datetime

from kafka import KafkaProducer

from config import (
    BOOTSTRAP_SERVERS,
    TOPIC_SENSORS,
    TEMPERATURE_RANGE,
    HUMIDITY_RANGE,
    PRODUCE_INTERVAL_SEC,
)


def main() -> None:
    # ID датчика — випадковий, але незмінний протягом цього запуску
    sensor_id = f"sensor-{uuid.uuid4().hex[:8]}"

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

    print(f"[producer] Sensor ID: {sensor_id}")
    print(f"[producer] Публікую в топік: {TOPIC_SENSORS}")
    print(f"[producer] Ctrl+C щоб зупинити\n")

    try:
        while True:
            payload = {
                "sensor_id": sensor_id,
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "temperature": round(random.uniform(*TEMPERATURE_RANGE), 2),
                "humidity": round(random.uniform(*HUMIDITY_RANGE), 2),
            }
            future = producer.send(TOPIC_SENSORS, key=sensor_id, value=payload)
            md = future.get(timeout=5)
            print(
                f"-> {payload}  (partition={md.partition}, offset={md.offset})"
            )
            time.sleep(PRODUCE_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\n[producer] Зупинено користувачем.")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
