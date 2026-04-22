#!/usr/bin/env bash
# Хелпер для ДЗ-5.
# Використання:
#   bash run.sh setup    # підняти Kafka в Docker + створити venv і топіки
#   bash run.sh topics   # лише перевірити/створити топіки
#   bash run.sh producer # запустити один датчик
#   bash run.sh proc     # запустити фільтр (processor.py)
#   bash run.sh alerts   # запустити споживача alert'ів
#   bash run.sh down     # зупинити Kafka container

set -e
cd "$(dirname "$0")"

VENV=".venv"

activate_venv() {
  if [ ! -d "$VENV" ]; then
    echo "▸ Створюю venv..."
    python3 -m venv "$VENV"
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
  else
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
  fi
}

case "${1:-}" in
  setup)
    echo "Піднімаю Kafka в Docker..."
    docker compose up -d
    echo "Чекаю поки broker стане доступний..."
    ready=false
    for i in $(seq 1 60); do
      # Перший фільтр — чи відкритий порт 9092 на host'і
      if ! (echo >/dev/tcp/localhost/9092) 2>/dev/null; then
        sleep 2
        continue
      fi
      # Другий — чи готовий broker відповідати на метадані
      if docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh \
             --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
        echo "   broker готовий (через $((i*2))s)"
        ready=true
        break
      fi
      sleep 2
    done
    if [ "$ready" != "true" ]; then
      echo "✖ broker не відповів за 2 хв. Логи:"
      docker compose logs kafka --tail 40
      exit 1
    fi
    sleep 2   # невеликий буфер для повної готовності контролера
    activate_venv
    echo "▸ Створюю топіки..."
    python create_topics.py
    ;;
  topics)
    activate_venv
    python create_topics.py
    ;;
  producer)
    activate_venv
    python producer.py
    ;;
  proc|processor)
    activate_venv
    python processor.py
    ;;
  alerts|alert|consumer)
    activate_venv
    python alert_consumer.py
    ;;
  down)
    docker compose down
    ;;
  *)
    echo "Usage: bash run.sh {setup|topics|producer|proc|alerts|down}"
    exit 1
    ;;
esac
