# Bewise Task 2
## Описание
___
Данный сервис предназначен для сохранения аудиозаписей пользователей. Пользователь регистрируется, получает токен и может отправить аудиозапись в формате .wav, которая будет преобразована в .mp3 формат и сохранена под уникальным UUID. Так же пользователь отправляет UUID другого пользователя (либо свой), к которому привязывается данная аудиозапись в базе данных.

<details>
<summary>ТЗ проекта ↓</summary>

Необходимо реализовать веб-сервис, выполняющий следующие функции:
Создание пользователя;
Для каждого пользователя - сохранение аудиозаписи в формате wav, преобразование её в формат mp3 и запись в базу данных и предоставление ссылки для скачивания аудиозаписи.

Детализация задачи:

С помощью Docker (предпочтительно - docker-compose) развернуть образ с любой опенсорсной СУБД (предпочтительно - PostgreSQL). Предоставить все необходимые скрипты и конфигурационные (docker/compose) файлы для развертывания СУБД, а также инструкции для подключения к ней. Необходимо обеспечить сохранность данных при рестарте контейнера (то есть - использовать volume-ы для хранения файлов СУБД на хост-машине.
Реализовать веб-сервис со следующими REST методами:
Создание пользователя, POST:
Принимает на вход запросы с именем пользователя;
Создаёт в базе данных пользователя заданным именем, так же генерирует уникальный идентификатор пользователя и UUID токен доступа (в виде строки) для данного пользователя;
Возвращает сгенерированные идентификатор пользователя и токен.
Добавление аудиозаписи, POST:
Принимает на вход запросы, содержащие уникальный идентификатор пользователя, токен доступа и аудиозапись в формате wav;
Преобразует аудиозапись в формат mp3, генерирует для неё уникальный UUID идентификатор и сохраняет их в базе данных;
Возвращает URL для скачивания записи вида http://host:port/record?id=id_записи&user=id_пользователя.
Доступ к аудиозаписи, GET:
Предоставляет возможность скачать аудиозапись по ссылке из п 2.2.3.
Для всех сервисов метода должна быть предусмотрена предусмотрена обработка различных ошибок, возникающих при выполнении запроса, с возвращением соответствующего HTTP статуса.
Модель данных (таблицы, поля) для каждого из заданий можно выбрать по своему усмотрению.
В репозитории с заданием должны быть предоставлены инструкции по сборке докер-образа с сервисами из пп. 2. и 3., их настройке и запуску. А также пример запросов к методам сервиса.
Желательно, если при выполнении задания вы будете использовать docker-compose, SQLAlchemy,  пользоваться аннотацией типов.
</details>

## Используемые технологии
___
![AppVeyor](https://img.shields.io/badge/Python-3.10.6-green)
![AppVeyor](https://img.shields.io/badge/FastAPI-0.95.2-9cf)
![AppVeyor](https://img.shields.io/badge/Alembic-1.11.0-9cf)
![AppVeyor](https://img.shields.io/badge/SQLAlchemy-2.0.13-9cf)
![AppVeyor](https://img.shields.io/badge/pytest-7.3.1-9cf)

![AppVeyor](https://img.shields.io/badge/Docker-20.10.21-green)
![AppVeyor](https://img.shields.io/badge/docker--compose-1.29.2-9cf)

![AppVeyor](https://img.shields.io/badge/Postgres-15.0-green)

## Модели
___

[![imageup.ru](https://imageup.ru/img221/4350581/my-first-board.jpg)](https://imageup.ru/img221/4350581/my-first-board.jpg.html)

## Запуск
___
###  Локально

1. Клонируем репозиторий:
   ```bash
   git clone https://github.com/Timoha23/bewise_task_2.git
   ```

2. Создаем .env файл и заполняем в соответствии с примером (.env.example).
3. Создаем и активируем виртуальное окружение:
   ```bash
    python -m venv venv
   ```
   ```bash
   source venv/Scripts/activate
   ```
4. Устанавливаем зависимости:
    ```bash
    pip install -r -requirements.txt
    ```
5. Запускаем приложение:
   ```bash
   python main.py
   ```
###  Докер
1. Клонируем репозиторий:
   ```bash
   git clone https://github.com/Timoha23/bewise_task_2.git
   ```

2. Создаем .env файл и заполняем в соответствии с примером (.env.example).
3. Поднимаем контейнеры:
   ```bash
   docker-compose up -d --build
   ```
4. Создаем и накатываем миграции:
   ```bash
   docker exec -it app alembic revision --autogenerate -m 'comment'
   ```
   ```bash
   docker exec -it app alembic upgrade head
   ```

## Примеры запросов
___
1. Регистраци пользователя
   * Endpoint: **host:port/user/**
   * Method: **POST**
   * Body: 
      ```json
      {
          "username": "<username>"
      }
        ```
   * Response: 
      ```json
      {
          "user_id": "<user_UUID>",
          "token": "<token>"
      }
      ```
   * Postman
     <details>
     <summary>Спойлер</summary>
      
     [![Пример запроса][1]][1]
      
     [1]: https://imageup.ru/img300/4350678/bw2_create_user.jpg
     </details>

1. Добавление аудиозаписи
   * Endpoint: **host:port/record/**
   * Method: **POST**
   * Params: 
      ```json
      {
          "user_id": "<user_UUID>"
      }
      ```
   * Files:
      ```
      {
          "file": ("<filename>", <wav_file>, "audio/wav")
      }
      ```
   * Headers:
      ```json
      {
          "Authorization": "Bearer <token>"
      }
      ```
   * Response: 
      ```json
      {
          "link": "http://host:port/record/?id=<audio_UUID>&user=<user_UUID>"
      }
      ```
   * Postman
     <details>
     <summary>Спойлер</summary>
      
     [![Передаем параметры][2]][2]
      
     [2]: https://imageup.ru/img226/4350679/bw2_post_audio_params.jpg
     [![Передаем токен][3]][3]
      
     [3]: https://imageup.ru/img226/4350680/bw2_post_audio_auth.jpg

     [![Передаем файл в теле запроса][4]][4]
      
     [4]: https://imageup.ru/img236/4350681/bw2_post_audio_body.jpg

     [![Отправляем запрос и получаем ответ][5]][5]
      
     [5]: https://imageup.ru/img291/4350682/bw2_post_audio_resp.jpg
     
     </details> 

2. Получение аудиозаписи
   * Endpoint: **host:port/record/**
   * Method: **GET**
   * Params: 
      ```json
      {
        "id": "<audio_UUID>",
        "user": "<user_UUID>",
      }
      ```
   * Response: 
      ```
      audiofile.mp3
      ```
   * Postman 
     <details>
     <summary>Спойлер</summary>
      
     [![Пример запроса][6]][6]
      
     [6]: https://imageup.ru/img10/4350676/bw2_get_audio_resp.jpg
     </details>
