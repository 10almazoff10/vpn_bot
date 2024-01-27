CREATE TABLE users (
    id SERIAL,
    telegram_id text,
	name text,
    date_first_enter date,
    status smallint,
	key_id smallint,
	balance float(2) NOT NULL DEFAULT 0
);

CREATE TABLE users_vpn_keys (
    key_id smallint,
    user_name text,
    access_url text,
    date_reg timestamp without time zone,
    date_out timestamp without time zone
);

CREATE TABLE operation_buffer (
    user_id smallint NOT NULL,
    summ numeric NOT NULL
);

CREATE TABLE operation_types (
    id SERIAL,
    type_name text
);

CREATE TABLE operations (
    id SERIAL,
    summ numeric,
    type smallint,
    operation_date timestamp without time zone,
    user_id integer
);

CREATE TABLE support_tasks (
    id SERIAL,
    telegram_id text,
    message text,
    date_create timestamp without time zone,
    state smallint DEFAULT 1
);

INSERT INTO operation_types (id, type_name) VALUES
(1, 'Списание'),
(2, 'Пополнение'),
(3, 'Создание счета'),
(4, 'Ежедневное списание за пользование VPN'),
(5, 'Корректировка счета');
