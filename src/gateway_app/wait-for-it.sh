#!/usr/bin/env bash
# wait-for-it.sh

set -e

# Установка netcat, выполнение очистки и удаление netcat
install_and_remove_netcat() {
  apt-get update && \
  apt-get install -y netcat-openbsd && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
}

# Функция для ожидания доступности сервиса
wait_for() {
  host="$1"
  port="$2"
  shift 2
  until nc -z "$host" "$port"; do
    >&2 echo "Service at $host:$port is unavailable - sleeping"
    sleep 1
  done
  >&2 echo "Service at $host:$port is up - executing command"
}

# Установка netcat и удаление после проверки
install_and_remove_netcat

# Ожидание всех указанных сервисов, переданных как аргументы
while [ "$1" != "--" ]; do
  IFS=: read -r host port <<< "$1"
  wait_for "$host" "$port"
  shift
done

# Удаляем разделитель '--'
shift

# Запуск основного приложения
exec "$@"
