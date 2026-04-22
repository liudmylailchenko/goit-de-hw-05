"""
Крок 4. Підписується на обидва alert-топіки й друкує сповіщення на екран.

Використання:  python alert_consumer.py
"""
import json

from kafka import KafkaConsumer

from config import (
    BOOTSTRAP_SERVERS,
    TOPIC_TEMPERATURE_ALERTS,
    TOPIC_HUMIDITY_ALERTS,
)


def main() -> None:
    consumer = KafkaConsumer(
        TOPIC_TEMPERATURE_ALERTS,
        TOPIC_HUMIDITY_ALERTS,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="hw05-alert-consumer",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )

    print(f"[alert-consumer] Слухаю:\n"
          f"   - {TOPIC_TEMPERATURE_ALERTS}\n"
          f"   - {TOPIC_HUMIDITY_ALERTS}\n")

    try:
        for record in consumer:
            topic = record.topic
            alert = record.value
            metric = alert.get("metric", "?").upper()
            sensor_id = alert.get("sensor_id")
            value = alert.get("value")
            ts = alert.get("timestamp")
            message = alert.get("message")

            print(
                f"[{topic}] {metric}  sensor={sensor_id}  value={value}  "
                f"at {ts}  ||  {message}"
            )
    except KeyboardInterrupt:
        print("\n[alert-consumer] Зупинено користувачем.")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
