Сервис по сокращению длинных ссылок. Если пользователь регистрируется, то можно увидеть аналитику по своим ссылкам.

#### Основные функции
- Создание короткой ссылки
- Редирект на полную ссылку по короткой
- Указание времени жизни короткой ссылки
- Регистрация и авторизация
- Просмотр своих ссылок и удаление
- Аналитика по своим ссылкам
  - Количество переходов
  - Количество переходов в разрезе уникальных IP

#### Стек технологий
- Фронтенд:
  - HTML, CSS, JavaScript
  - Bootstrap для стилизации и адаптивного дизайна
  - Fetch API для взаимодействия с бэкендом

- Бэкенд:
  - Python
  - FastAPI
  - Pydantic
  - Alembic для миграций
  - JWT-токены для аутентификации

- База данных
  - PostgreSQL

- Инфраструктура:
  - Docker, Docker Compose
  - GitHub (для хранения кода)

#### Установка и запуск

- Предварительные требования
  - Установите Docker и Docker Compose
  - Убедитесь, что порты 8000 (бэкенд) и 80 (фронтенд) свободны

- Инструкции по запуску
  - Клонируйте репозиторий:
    - git clone <repository>
  - Перейдите в папку проекта
    - cd shorterLink
  - Укажите желаемые параметры для подключения к PostgreSQL в файле .env (для запуска проекта из docker-compose могут быть любыми)
  - Запустите проект с помощью Docker Compose:
    - docker compose up --build
  - Выполните миграции БД
    - docker compose -f docker-compose.yml exec web alembic upgrade head

 Демо проекта доступно по ссылке - http://url-shorter/forb1.tech/index.html (user/123)
