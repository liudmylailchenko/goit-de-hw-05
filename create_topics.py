"""
Крок 1. Створює три топіки в Kafka:
  - building_sensors_zhuk_liudmyla
  - temperature_alerts_zhuk_liudmyla
  - humidity_alerts_zhuk_liudmyla

Використання:  python create_topics.py

Вивід містить також список усіх топіків, що підпадають під фільтр із завдання:
    [print(topic) for topic in admin_client.list_topics() if "my_name" in topic]
щоб скриншот можна було зробити одразу після створення.
"""
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from config import (
    BOOTSTRAP_SERVERS,
    NAME_SUFFIX,
    TOPIC_SENSORS,
    TOPIC_TEMPERATURE_ALERTS,
    TOPIC_HUMIDITY_ALERTS,
)


def main() -> None:
    admin_client = KafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        client_id="hw05-admin",
    )

    topics_to_create = [
        NewTopic(name=TOPIC_SENSORS, num_partitions=2, replication_factor=1),
        NewTopic(name=TOPIC_TEMPERATURE_ALERTS, num_partitions=2, replication_factor=1),
        NewTopic(name=TOPIC_HUMIDITY_ALERTS, num_partitions=2, replication_factor=1),
    ]

    for new_topic in topics_to_create:
        try:
            admin_client.create_topics(new_topics=[new_topic], validate_only=False)
            print(f"Створено топік: {new_topic.name}")
        except TopicAlreadyExistsError:
            print(f"Топік уже існує: {new_topic.name}")

    # Перевірка — показуємо лише «наші» топіки (з особистим суфіксом)
    print("\nТопіки з суфіксом", NAME_SUFFIX, ":")
    [print(topic) for topic in admin_client.list_topics() if NAME_SUFFIX in topic]

    admin_client.close()


if __name__ == "__main__":
    main()
