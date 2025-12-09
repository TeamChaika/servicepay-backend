# Инструкция по развертыванию

## Проблема с volumes

Некоторые платформы развертывания (Timeweb Cloud, Railway, Render и т.д.) не разрешают использование `volumes` в `docker-compose.yml`.

## Решение

Основной `docker-compose.yml` настроен для production развертывания **без volumes**.

### Что изменено:

1. ✅ Удалены все `volumes` секции
2. ✅ Удалена секция `volumes:` в конце файла
3. ✅ Переменные окружения передаются через `environment:` вместо `env_file:`
4. ✅ Команда backend изменена с `--reload` на обычный запуск (без hot-reload)

### Для локальной разработки

Используйте `docker-compose.dev.yml` для разработки с hot-reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Это добавит:
- Volumes для PostgreSQL и Redis (персистентность данных)
- Volumes для монтирования кода (hot-reload)
- Использование `.env` файла через `env_file`

## Настройка переменных окружения

### Вариант 1: Файл .env (для локального развертывания)

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` и заполните все переменные

### Вариант 2: Переменные окружения платформы (для облачного развертывания)

Установите все переменные окружения в настройках вашей платформы развертывания.

**Обязательные переменные:**
```
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-32-byte-base64-key
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/helpchaika
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-jwt-secret
API_BASE_URL=https://your-api-domain.com
ADMIN_PORTAL_URL=https://your-admin-domain.com
GUEST_PORTAL_URL=https://your-guest-domain.com
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
EMAIL_FROM=noreply@example.com
EMAIL_FROM_NAME=ServicePay
```

## Развертывание на Timeweb Cloud

1. Подключите репозиторий `servicepay-backend`
2. Установите все переменные окружения в настройках приложения
3. Убедитесь, что `docker-compose.yml` не содержит `volumes`
4. Запустите развертывание

## Важные замечания

⚠️ **Без volumes:**
- Данные PostgreSQL будут храниться только в контейнере (потеряются при перезапуске)
- Данные Redis будут храниться только в контейнере (потеряются при перезапуске)
- Для production рекомендуется использовать внешние managed сервисы для БД и Redis

### Рекомендации для production:

1. Используйте managed PostgreSQL (например, от Timeweb, AWS RDS, etc.)
2. Используйте managed Redis (например, Redis Cloud, AWS ElastiCache, etc.)
3. Обновите `DATABASE_URL` и `REDIS_URL` на внешние сервисы
4. Удалите сервисы `postgres` и `redis` из `docker-compose.yml` или используйте внешние

Пример для внешних сервисов:

```yaml
services:
  backend:
    # ... остальная конфигурация
    environment:
      - DATABASE_URL=postgresql://user:pass@external-db:5432/dbname
      - REDIS_URL=redis://external-redis:6379/0
    # Удалите depends_on для postgres и redis
```

## Проверка развертывания

После развертывания проверьте:

1. ✅ Backend доступен: `curl http://your-domain:8000/health`
2. ✅ API документация: `http://your-domain:8000/docs`
3. ✅ Логи без ошибок: `docker-compose logs backend`
4. ✅ Celery worker работает: `docker-compose logs celery-worker`
5. ✅ Celery beat работает: `docker-compose logs celery-beat`
