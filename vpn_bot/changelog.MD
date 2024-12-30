### 2.3.0 30.12.2024
- Тариф вынесен в конфиг
- Обновлен текст на кнопках
- Улучшена структура кода, косметические улучшения

### 2.2.3 03.11.2024
- Фикс ошибки, когда блокировка сервера не удаляла ключи

### 2.2.2 20.10.2024
- Переработан вывод статистики в виде таблиц

### 2.2.1 03.10.2024
- Добавлено отображение страны в списке серверов

### 2.2.0 29.09.2024
- Добавлена возможность пользователям управлять серверами к которым они подключаются
```postgres-sql
alter table public.users_vpn_keys add if not exists enabled BOOLEAN default true;
```

## 2.1.2 24.09.2024
- Оптимизация кода API

### 2.1.1.1 14.09.2024
- Фикс ошибки во время обновление трафика пользователей

### 2.1.1 11.09.2024
- Фикс ошибки регистрации нового пользователя

### 2.1.0 07.09.2024
- Переработан механизм обслуживания ключей
- Переработан логгер

### 2.0.5 30.08.2024
- Фикс механизма получения трафика
```sql
alter table public.users add if not exists traffic BIGINT;
ALTER TABLE users_vpn_keys ALTER COLUMN traffic TYPE bigint USING traffic::bigint;
```

### 2.0.4 27.08.2024
- Расширена статистика по запросам на API
```sql
alter table public.users_stat add if not exists country varchar(30);
alter table public.users_stat add if not exists region varchar(30);
alter table public.users_stat add if not exists city varchar(30);
```+
### 2.0.3 25.08.2024
- Вернул функционал получения трафика по ключам
```sql
alter table outline_servers add column server_ip text;
```

### 2.0.2 25.08.2024
- Исправлен баг, когда зарегистрированный, забаненный пользователь пополнял счет через админа, но он не разблокировался

### 2.0.1 21.08.2024
- Исправлен баг, когда зарегистрированный, забаненный пользователь пополнял счет, но он не разблокировался
- Исправлен баг, когда пользователь без логина не мог зарегистрироваться

### 2.0.0 20.08.2024
- Реализован функционал одновременно динамических и статических ключей
- Множественные улучшения кода с визуальной точки зрения

```sql
TRUNCATE users_vpn_keys;
ALTER TABLE public.users_vpn_keys RENAME COLUMN user_name TO telegram_id;
ALTER TABLE public.users_vpn_keys ADD "method" text NULL;
ALTER TABLE public.users_vpn_keys ADD "password" text NULL;
ALTER TABLE public.users_vpn_keys ADD CONSTRAINT users_vpn_keys_unique UNIQUE ("password");
ALTER TABLE public.users_vpn_keys ADD "server" text NULL;
ALTER TABLE public.users_vpn_keys ADD server_port int NULL;
ALTER TABLE public.users_vpn_keys ADD server_id int NULL;

```

### 1.5.0 02.08.2024
- Улучение визуальности кода
- Добавлен класс monitoring, для получения информации о системе во время запуска

### 1.4.9 28.07.2024
- Добавлено логирование DEBUG сообщений в отдельный файл

### 1.4.8 24.07.2024
- Исправлена функция удаления ключей
- Исправлена текстовка при авторизации нового пользователя

### 1.4.7 21.07.2024
- Расширено логирование, добавлен ip адрес подключаемого пользователя
- Изменено отображение заблокированных пользователей, теперь отображается только их количество
- Создан механизм очистки серверов от старых ключей, будет запускаться каждый день в 03:00

```sql
ALTER TABLE IF EXISTS public.users_stat
    ADD COLUMN ip text;
```

### 1.4.6 20.07.2024
- Расширена статистика - добавлена статистика подключений по пользователям

### 1.4.5 17.07.2024
- Исправлен тип данных в таблице событий с date на timestamp
- Создана таблица в БД содержащая версию бота

```sql
ALTER TABLE users_stat
ALTER COLUMN date TYPE TIMESTAMP;

CREATE TABLE public.bot_version (
	id int GENERATED ALWAYS AS IDENTITY NOT NULL,
	"version" text NOT NULL,
	"date" timestamp NULL,
	CONSTRAINT bot_version_pk PRIMARY KEY (id),
	CONSTRAINT bot_version_unique UNIQUE ("version")
);

insert into bot_version (version, date) values ('1.4.5', (select now()));
```

1.4.4 27.06.2024
- Расширено логирование Api
- Исправлена ошибка, при котороый пользователь не мог получить ключ из-за того что какой либо из серверов не отвечает

```
CREATE TABLE public.users_stat (
	id int GENERATED ALWAYS AS IDENTITY NOT NULL,
	telegram_id text NOT NULL,
	stat_name text NULL,
	"date" date NULL,
	CONSTRAINT users_stat_pk PRIMARY KEY (id)
);
```

1.4.3 19.06.2024
- Добавлен функционал сжатия логов
- Удален некоторый не используемый код
- Исправлена ошибка запроса которая рассылала всем пользователям у которых УЗ уже заблокирована сообщение о блокировке
- В запуск background добавлена проверка подключения к БД


1.4.2 18.06.2024
- Исправлен текст приветствия
- Добавлена кнопка рассылки на клавиатуру админа
- Изменен вывод при блокировке пользователей

1.4.1 12.06.2024
- Добавлена функция рассылки
- Оптимизация кода

1.4.0 09.06.2024
- Система переписана для использования динамических ключей!
- Создан Api для выдачи ключей от серверов.

```
ALTER TABLE IF EXISTS public.users
    ADD COLUMN user_key text;


CREATE TABLE public.outline_servers
(
    id smallint,
    name text NOT NULL,
    comment text NOT NULL,
    country text NOT NULL,
    speed_in_kbytes integer NOT NULL,
    connection_link text NOT NULL,
    creation_date date NOT NULL,
    standby_status boolean NULL,
    active_keys int DEFAULT 0 NULL,
    PRIMARY KEY (id)
);
```
1.3.1 2024.05.20
- Добавлен новый статус операции 6 для пополнений через форму оплаты
- Небольшие исправления читаемости кода
- Значение Telegram-id администратора вынесено в конфиг файл
Update:
sql: insert into operation_types values ('6', 'Пополнение через форму оплаты');
config: для параметра телеграм добавить   admin_id: 758952233

1.3.0 2024.05.13
- Добавлена оплата через сервис yookassa!

1.2.4 2024.05.06
- Исправлена ошибка, когда пользователи с балансом = 5 не блокировались
- Добавлено отображение трафика ключа

1.2.3 2024.05.01
- Добавлен статус пользователей
```
    alter table users add column user_state int2 default 0 not null;
```

1.2.2 - 2024.04.29
- Добавлена отправка автоматических сообщений при пополнении баланса
update:
    ```
    ALTER TABLE operation_buffer
        ALTER COLUMN summ TYPE INTEGER;

    ```
1.2.1 27.04.2024
- Исправлен способ подключения к БД
- Добавлена проверка имени пользователя при регистрации, чтобы небыло возможности для SQL инъекций
- Рефакторинг кода

1.2.0 6.04.2024
- добавлена возможность отправлять сообщения пользователям
- удален функционал работы с ключами, так как в нем нет необходимости

1.0.2 13.03.2024
Изменена структура бота:
- файлы перенесены в отдельные модули
- конфигурационный файл вынесен в отдельный yaml файл

1.0.1 18.02.2024
Устранена ошибка, когда пользователь заблокировал бота, и отправка сообщения вела к крашу бота 

1.0.0 15.02.2024
Бот полностью перенесен в Докер


0.1.6 27.01.2024
Переработка бота, удалены токены авторизации, добавлена возможность генерации нового ключа
Создан sql скрипт формирующий БД