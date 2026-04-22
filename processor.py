"""
Крок 3. Читає повідомлення з building_sensors_zhuk_liudmyla, фільтрує їх
і пересилає сповіщення:
  - temperature_alerts_zhuk_liudmyla — якщо температура > 40 °C
  - humidity_alerts_zhuk_liudmyla    — якщо вологість > 80 % або < 20 %

Використання:  python processor.py
"""
import json
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer

from config import (
    BOOTSTRAP_SERVERS,
    TOPIC_SENSORS,
    TOPIC_TEMPERATURE_ALERTS,
    TOPIC_HUMIDITY_ALERTS,
    TEMPERATURE_THRESHOLD,
    HUMIDITY_MIN,
    HUMIDITY_MAX,
)


def make_alert(sensor_id: str, ts: str, metric: str, value: float, message: str) -> dict:
    return {
        "sensor_id": sensor_id,
        "timestamp": ts,
        "alert_generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "metric": metric,
        "value": value,
        "message": message,
    }


def main() -> None:
    consumer = KafkaConsumer(
        TOPIC_SENSORS,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="hw05-processor",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

    print(f"[processor] Слухаю: {TOPIC_SENSORS}")
    print(f"[processor] Пороги: temp>{TEMPERATURE_THRESHOLD}°C, "
          f"humidity <{HUMIDITY_MIN}% або >{HUMIDITY_MAX}%\n")

    try:
        for record in consumer:
            data = record.value
            sensor_id = data.get("sensor_id")
            ts = data.get("timestamp")
            temperature = float(data.get("temperature", 0))
            humidity = float(data.get("humidity", 0))

            print(
                f"<- sensor={sensor_id} t={temperature}°C h={humidity}% "
                f"(partition={record.partition}, offset={record.offset})"
            )

            # --- Температура ---
            if temperature > TEMPERATURE_THRESHOLD:
                alert = make_alert(
                    sensor_id, ts, "temperature", temperature,
                    f"Temperature {temperature}°C exceeds threshold {TEMPERATURE_THRESHOLD}°C",
                )
                producer.send(TOPIC_TEMPERATURE_ALERTS, key=sensor_id, value=alert)
                print(f"   🔥 -> {TOPIC_TEMPERATURE_ALERTS}: {alert['message']}")

            # --- Вологість ---
            if humidity > HUMIDITY_MAX or humidity < HUMIDITY_MIN:
                if humidity > HUMIDITY_MAX:
                    msg = f"Humidity {humidity}% exceeds max {HUMIDITY_MAX}%"
                else:
                    msg = f"Humidity {humidity}% below min {HUMIDITY_MIN}%"
                alert = make_alert(sensor_id, ts, "humidity", humidity, msg)
                producer.send(TOPIC_HUMIDITY_ALERTS, key=sensor_id, value=alert)
                print(f"   💧 -> {TOPIC_HUMIDITY_ALERTS}: {alert['message']}")

            producer.flush()
    except KeyboardInterrupt:
        print("\n[processor] Зупинено користувачем.")
    finally:
        consumer.close()
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
