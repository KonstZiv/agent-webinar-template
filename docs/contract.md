# Контракт v1 → v2

> **Приклад конкретного проєкту.** Домовленості між першою і другою версіями сайту вебінару. Друга версія зібрана на цьому шаблоні: [agent.pythoncourse.me](https://agent.pythoncourse.me), код — [agent-webinar-efir](https://github.com/KonstZiv/agent-webinar-efir). Тут — версія 1 від 10.10.2026; пізніша — у репозиторії другої версії сайту (`docs/contract.md`). Новий проєкт пише свій контракт або видаляє цей разом із `docs/legacy-schema.md` і `tests/test_contract.py` (README, «Як почати проєкт»).

**Версія 1 · 10.10.2026.** Домовленості, яких дотримує сайт v2, щоб замінити v1 на тих самих адресах без втрат: посилання з уже надісланих листів, cookie, аналітика, імпорт учасників. Записано за кодом v1 (репозиторій першої версії сайту, коміт `40b5de5`) і шаблону (`agent-webinar-template`, коміт `4a547d9`); v2 — проєкт із шаблону, пакет `app`. Шляхи файлів: «v1:» — від кореня репозиторію сайту, «шаблон:» — від кореня репозиторію шаблону. Вимоги до v2 понад цей документ — у вимогах і специфікації v2. Схема даних v1 і відповідність полів для імпорту — `docs/legacy-schema.md`.

Документ лежить в обох репозиторіях (`docs/contract.md`), копії однакові. Частину, яку вже виконує шаблон, тримає `tests/test_contract.py` шаблону: він читає з документа таблиці розділів 2 і 3, еталон і назву модуля розділу 4, рядок cookie розділу 5 і етап.

Тест перевіряє назви змінних і наявність маршрутів, а також такі «храповики»:

- модуль токена (розділ 4);
- префікс шляхів із токеном (розділ 10);
- cookie (розділ 5);
- етап.

Поведінку маршрутів і змінних перевіряють тести зрізів v2. «ні» в стовпці «У шаблоні» означає, що в шаблоні цього ще немає, і тест вимагає саме цього. Зріз v2, що додає змінну чи маршрут, змінює позначку на «так».

Етап: `розробка`. Значення — `розробка` або `запуск`. На етапі `запуск` тест падає, якщо:

- у таблицях розділів 2 і 3 лишився хоч один рядок «ні»;
- у `consent.js` немає рядка cookie розділу 5. Етап перемикає задача запуску v2.

## Адреси

- `https://agent.pythoncourse.me` — зараз шаблон у режимі переадресації (307) на v1; з етапу 10 ефіру 21.10 — v2.
- `https://agent-preparation.pythoncourse.me` — v1; після ефіру домен переходить на сервіс v2.
- Порядок імпорту і перемикання адрес — `docs/legacy-schema.md`, «Порядок імпорту і перемикання адрес».
- Посилання в листах v1 (трансляція, календар, відписка, політика) побудовано від `PUBLIC_BASE_URL`; у текстах листів це `https://agent.pythoncourse.me/…`. Заголовок `List-Unsubscribe` побудовано від `SERVICE_BASE_URL`, власної адреси v1 (v1: `src/webinar/adapters/mail/confirmation.py`, `JinjaConfirmationComposer`; `docs/copy.md`, розділи 3 і 6). Тому після переходу домену спільні шляхи розділу 3 на обох адресах обслуговує v2.

## 1. Пакет і запуск

| | v1 | Шаблон і v2 |
| :-- | :-- | :-- |
| Пакет | `webinar`, код у `src/webinar/` (v1: `pyproject.toml`) | `app`, код у `src/app/` (шаблон: `pyproject.toml`) |
| Запуск на Railway | `web: uvicorn webinar.main:create_app --factory --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips '*'` (v1: `Procfile`) | те саме з `app.main:create_app` (шаблон: `Procfile`) |
| Запуск локально | `docker compose up -d` (база), далі `uv run --env-file .env uvicorn webinar.main:create_app --factory --reload` (v1: `CLAUDE.md`) | те саме з `app.main:create_app` (шаблон: `CLAUDE.md`, `README.md`) |
| Міграції | `alembic upgrade head` — команда перед деплоєм у Railway (v1: `CLAUDE.md`, «Команди») | те саме (шаблон: `CLAUDE.md`, «Команди») |

Застосунок збирає фабрика `create_app` (v1: `src/webinar/main.py`; шаблон: `src/app/main.py`). Застосунку на рівні модуля немає; налаштування й залежності передаються явно.

## 2. Змінні середовища

Назва змінної — назва поля `Settings` великими літерами, без префікса: pydantic-settings без `env_prefix` (v1: `src/webinar/settings.py`; шаблон: `src/app/settings.py`, `_ENV_CONFIG`). Назви з префіксом `APP_` читаються без нього: `APP_X` → `X`. Нові змінні v2 називаються за цим правилом. Перелік змінних без значень — `docs/env.example` кожного репозиторію.

Спільна змінна має ту саму назву і те саме значення у v1 і v2.

| Змінна | У шаблоні | v1 | Між v1 і v2 |
| :-- | :-- | :-- | :-- |
| `UNSUBSCRIBE_SECRET` | ні — додає v2 | обов'язкова, щонайменше 32 символи | спільна: з іншим значенням токени зі старих листів не пройдуть перевірку (розділ 4) |
| `GA4_MEASUREMENT_ID` | так | обов'язкова | спільна в продакшні: v1 і v2 надсилають події в ресурс GA4 `agent-prod`, тож `generate_lead` рахується раз на браузер для обох сайтів (розділ 5), а звіти не розриваються. Виняток — staging v2: тестовий ресурс `agent-staging`. Джерело — рішення автора, 10.10.2026 |
| `DATABASE_URL` | так | обов'язкова | назва та сама; значення своє — у кожного сервісу своя база |
| `REDIRECT_BASE_URL` | так | читається, але не використовується | назва та сама; режим переадресації є лише в шаблоні (розділ 7) |
| `INDEXING_ENABLED` | так | необов'язкова | назва та сама; значення — налаштування сервісу |
| `TURNSTILE_SITE_KEY` | так | обов'язкова | назва та сама; значення — налаштування сервісу |
| `TURNSTILE_SECRET_KEY` | так | обов'язкова | назва та сама; значення — налаштування сервісу |
| `TURNSTILE_ALLOWED_HOSTNAMES` | так | необов'язкова | назва та сама; значення — налаштування сервісу |
| `RAILWAY_GIT_COMMIT_SHA` | так | необов'язкова | ставить Railway |
| `PORT` | так | є в `docs/env.example` | ставить Railway; читає `Procfile`, а не `Settings` |

Лише у v1, без вимог до v2: `PUBLIC_BASE_URL`, `SERVICE_BASE_URL`, `PAGE_MODE`, `STREAM_URL`, `RECORDING_YOUTUBE_ID`, `EVENT_START`, `EVENT_END`, `REMINDERS_ENABLED`, `RESEND_API_KEY`, `SENDER_EMAIL`, `ADMIN_TOKEN` (токен адміністратора v2 — власний, розділ 8).

## 3. Спільні шляхи

Модулі маршрутів: v1 — `src/webinar/adapters/web/routers/`, шаблон — `src/app/adapters/web/routers/`.

| Шлях | Методи | У шаблоні | v1 | Що робить |
| :-- | :-- | :-- | :-- | :-- |
| `/` | GET | так — `home.py`, службова сторінка | `landing.py` — лендінг | головна сторінка |
| `/privacy` | GET | так — `privacy.py` | `privacy.py` | політика приватності з `docs/legal/privacy.md` |
| `/healthz` | GET | так — `health.py`, відповідає ще й на HEAD | `health.py` | 200 `{"status": "ok"}`, коли база відповідає, інакше 503 `{"status": "unavailable"}`; перевірка працездатності Railway |
| `/go/stream` | GET | ні — додає v2 | `stream.py` | 302 на трансляцію; поки адреси трансляції немає — сторінка «посилання з'явиться»; посилання — у листах і події календаря |
| `/calendar.ics` | GET | ні — додає v2 | `calendar.py` | файл події (розділ 6); посилання — у листі |
| `/unsubscribe/{token}` | GET, POST | ні — додає v2 | `unsubscribe.py` | GET — сторінка підтвердження, нічого не змінює; POST — відписка з форми й одним кліком |

`GET /register` (v1: 303 на `/#register`, `src/webinar/adapters/web/routers/register.py`) не входить у контракт; чи обслуговувати його, вирішує v2.

Відписка у v1 (v1: `src/webinar/adapters/web/routers/unsubscribe.py`, `src/webinar/core/unsubscribe.py`; `spec.md`, «Відписка»):

- GET: токен правильний і учасник є — сторінка підтвердження з адресою; учасника вже немає — сторінка «відписано»; токен неправильний — 400. Тексти — `docs/copy.md` v1, 8.1–8.3.
- POST з форми сторінки видаляє учасника і показує сторінку «відписано»; повтор не дає помилки.
- POST одним кліком (RFC 8058) — тіло `List-Unsubscribe=One-Click` (`application/x-www-form-urlencoded` або `multipart/form-data`), відповідь 200 без тіла. Лист несе `List-Unsubscribe: <…/unsubscribe/{token}>` і `List-Unsubscribe-Post: List-Unsubscribe=One-Click`.
- Неправильний токен — 400; база недоступна — 503.
- Токен не виходить за межі сайту: `Referrer-Policy: no-referrer`, на сторінках відписки немає Google Analytics, у журналі доступу шлях маскується (`/unsubscribe/***`). Cookie `src` v1 тут не ставить.

## 4. Токен відписки

Формат (v1: `src/webinar/core/unsubscribe.py`, `make_token`, `read_token`):

- вигляд `<id>.<sig>`, 76 символів ASCII;
- `id` — `unsubscribe_id` учасника (UUID) як 32 шістнадцяткові символи в нижньому регістрі (`uuid.hex`);
- `sig` — base64url без `=` (43 символи) від HMAC-SHA256 з ключем `UNSUBSCRIBE_SECRET` (UTF-8) над рядком `unsubscribe:<id>`;
- перевірка порівнює підпис зі сталим часом; будь-який інший рядок — неправильний токен;
- адреси в токені немає. Токен — дозвіл видалити учасника, тож у журнали застосунку він не потрапляє: журнал доступу маскує шлях. Журнали HTTP на краю Railway показують шлях повністю — це поза застосунком.

`UNSUBSCRIBE_SECRET` у v2 має те саме значення (розділ 2), а `unsubscribe_id` кожного учасника переноситься у v2 без змін (`docs/legacy-schema.md`). Тоді v2 приймає токен зі старого листа і знаходить того самого учасника.

Реалізація у v2 — модуль, названий нижче, з функціями як у v1: `make_token(unsubscribe_id: uuid.UUID, secret: str) -> str` і `read_token(token: str, secret: str) -> uuid.UUID | None`.

- Поки рядок `/unsubscribe/{token}` розділу 3 має «ні», модуля немає.
- Коли рядок має «так», `tests/test_contract.py` імпортує обидві функції і звіряє їх з еталоном. Застосунок тест будує із секретом еталону; GET з еталонним токеном не має давати 400.

- модуль у v2 (функції `make_token` і `read_token`): `app.core.unsubscribe`

Еталонний приклад обчислено функцією `make_token` v1 (коміт `40b5de5`). Секрет вигаданий, він лише для перевірки реалізацій:

- секрет (лише для прикладу): `contract-example-secret-not-for-production`
- `unsubscribe_id`: `5d0c8a3e-2f4b-4c6d-9e1a-7b8c9d0e1f2a`
- токен: `5d0c8a3e2f4b4c6d9e1a7b8c9d0e1f2a.uX_9-ez7y6fohHOrJe2IvD76_hYYKNxF8VemVukndi4`

## 5. Cookie `webinar_lead`

- рядок cookie: `webinar_lead=1; Domain=.pythoncourse.me; Path=/; Max-Age=31536000; Secure; SameSite=Lax`
- у шаблоні: ні — повертає зріз «реєстрація» v2 (розділ 10)

Поки в шаблоні cookie немає, `consent.js` не містить `webinar_lead`. Коли вона з'явиться, позначка стає «так», і рядок cookie в `consent.js` має побайтово збігатися з рядком вище. На етапі `запуск` цей рядок має бути в `consent.js` за будь-якої позначки. Усі три правила перевіряє `tests/test_contract.py`.

- Назва — `webinar_lead`, значення — `1`. Домен `.pythoncourse.me` охоплює всі піддомени, тож cookie бачать і v1, і v2. Строк — рік (31 536 000 с). Без `HttpOnly`: cookie ставить і читає скрипт (v1: `src/webinar/adapters/web/static/js/consent.js`, `LEAD_COOKIE_NAME`, `LEAD_COOKIE`, `reportLead`).
- Подію `generate_lead` надсилає екран успіху реєстрації, лише коли аналітика активна і cookie немає. Cookie ставиться після того, як gtag надіслав подію (`event_callback`). Якщо gtag заблоковано, cookie не з'являється, і наступна реєстрація, тут чи на v2, ще може повідомити про лід. Перегляд сторінки події не дає.
- Разом зі спільним `GA4_MEASUREMENT_ID` (розділ 2) це дає один `generate_lead` на браузер для обох сайтів.
- Шаблон зараз: `src/app/adapters/web/static/js/consent.js` не містить ні `generate_lead`, ні `webinar_lead`.

## 6. Адреса клієнта і подія календаря

- Адреса клієнта, ключ обмеження частоти, — із заголовка `X-Real-IP`: проксі Railway ставить його сам. Береться останнє значення, якщо це коректна IP-адреса, інакше — адреса з'єднання. `X-Forwarded-For` не використовується: з `--forwarded-allow-ips '*'` uvicorn бере його крайній лівий запис, який задає клієнт. Код — `client_ip`, логіка однакова (v1: `src/webinar/adapters/web/client_ip.py`; шаблон: `src/app/adapters/web/client_ip.py`).
- Ідентифікатор події календаря — `UID` `webinar-2026-10-20@pythoncourse.me`, сталий і без «v1» (v1: `src/webinar/adapters/web/ics.py`, `EVENT_UID`). `/calendar.ics` v2 віддає подію з тим самим `UID`: календар, куди подію вже додали, оновить її, а не створить другу.
- `UID` сталий. `SEQUENCE` збільшується, коли змінюється час або опис події: після перенесення ефіру на 21.10 v1 віддає `SEQUENCE:1` з початком 21.10, тож v2 віддає `SEQUENCE` не менший за 1. `DTSTAMP` — час створення файла (v1: `src/webinar/adapters/web/ics.py`, `build_calendar`, `dtstamp` — поточний час).

## 7. Переадресація

Правило шаблону (шаблон: `src/app/adapters/web/redirect.py`, `RedirectEverything`, `redirect_location`; `README.md`, «Режим переадресації»):

- непорожня `REDIRECT_BASE_URL` (корінь сайту `https://вузол`) — кожен запит будь-яким методом, крім `/healthz`, отримує 307;
- `Location` = `REDIRECT_BASE_URL` + шлях і параметри запиту побайтово, як їх надіслав клієнт; шлях без `/` на початку отримує `/`, тож адреса не виходить за вузол бази;
- 307 зберігає метод і тіло, тож POST відписки одним кліком доходить до цілі;
- переадресація тимчасова: `Cache-Control: no-store`, тіло порожнє. 301 і 308 не використовуються, бо адресу згодом обслуговуватиме інший сайт;
- поки `INDEXING_ENABLED` вимкнено, відповідь несе `X-Robots-Tag: noindex`.

У v1 режиму переадресації немає: після ефіру домен agent-preparation переходить на сервіс v2.

## 8. Адміністратор

- Маршрути v1: `GET /admin/stats` і `POST /admin/emails/retry` (v1: `src/webinar/adapters/web/routers/admin.py`). До спільних шляхів (розділ 3) вони не входять.
- Доступ — заголовок `Authorization: Bearer <токен>`. Назва схеми — без урахування регістру; токен порівнюється як байти зі сталим часом. Без заголовка або з неправильним токеном — однакова відповідь 401 `{"detail": "Unauthorized"}` із `WWW-Authenticate: Bearer` (v1: `src/webinar/adapters/web/admin_auth.py`, `require_admin`). У v1 токен задає `ADMIN_TOKEN`.
- Токен адміністратора v2 — власний, не той, що у v1. Назву змінної дає v2 (розділ 2).

## 9. Власність файлів і частини шаблонів сторінок

Правило власності файлів; шляхи — у шаблоні і v2:

- макет володіє `src/app/adapters/web/templates/landing.html` і текою `src/app/adapters/web/static/`;
- зрізи володіють частинами шаблонів сторінок `src/app/adapters/web/templates/_<назва>.html`; форма реєстрації — `src/app/adapters/web/templates/_form.html`;
- лендінг підключає частини за назвами з цього розділу і пропускає відсутні (`{% include "_form.html" ignore missing %}`);
- маршрути підключаються автоматично: кожен модуль пакета `src/app/adapters/web/routers/` експортує `router` (шаблон: `src/app/adapters/web/routing.py`, `discover_routers`; виклик — `src/app/main.py`).

Назви частин: `_form.html` — форма реєстрації. Інші назви додає v2.

Що вже є в шаблоні — інфраструктура, не частини зрізів:

- `src/app/adapters/web/templates/base.html` — каркас сторінки з блоками `title`, `meta`, `scripts`, `main`; підключає `src/app/adapters/web/templates/partials/footer.html` (футер: політика приватності, налаштування cookie) і `src/app/adapters/web/templates/partials/cookie_banner.html` (банер cookie);
- `src/app/adapters/web/templates/home.html` — службова сторінка `/`; `src/app/adapters/web/templates/privacy.html` — `/privacy`;
- у `src/app/adapters/web/static/`: `css/site.css` (нейтральні стилі), `js/consent.js` (банер cookie і Google Consent Mode v2), `js/htmx.min.js` (HTMX 2.0.11), `favicon.ico`. `consent.js` і `htmx.min.js` — файли шаблону в теці, яку правило віддає макету. Саме в `consent.js` повертається `generate_lead` (розділ 10).

`landing.html` і частин `_*.html` у шаблоні немає. У v1, для порівняння: `src/webinar/adapters/web/templates/landing.html`, форма — `src/webinar/adapters/web/templates/partials/register.html`.

## 10. Що прибрано з шаблону і має повернутись у v2

- **Подія `generate_lead` і cookie `webinar_lead`** (розділ 5).
  - У v1: `src/webinar/adapters/web/static/js/consent.js` (`reportLead`, `LEAD_COOKIE`) і позначка `data-lead` на екрані успіху (`src/webinar/adapters/web/templates/partials/register.html`).
  - У шаблоні `src/app/adapters/web/static/js/consent.js` їх не має.
  - Повертає зріз «реєстрація».
- **Префікс `/unsubscribe/` у переліку шляхів із токеном.**
  - У v1: `src/webinar/adapters/web/token_paths.py`, `UNSUBSCRIBE_PREFIX`.
  - У шаблоні `TOKEN_PATH_PREFIXES = ()` (`src/app/adapters/web/token_paths.py`).
  - Повертається разом із маршрутом `/unsubscribe/{token}` (правило `CLAUDE.md` шаблону: маршрут із токеном додається разом із префіксом). Тоді журнал доступу маскує токен, а сторінки відписки не завантажують Google Analytics.
  - `tests/test_contract.py` перевіряє: шлях зі `{token}`, позначений «так», лежить під префіксом із `TOKEN_PATH_PREFIXES`; позначений «ні» — ні.
- **Підключення Turnstile.**
  - У v1: `src/webinar/main.py` (`CloudflareTurnstile` у `create_app`); скрипт `https://challenges.cloudflare.com/turnstile/v0/api.js` у `src/webinar/adapters/web/templates/landing.html`; віджет `cf-turnstile` у `src/webinar/adapters/web/templates/partials/register.html`; перевірка на сервері — `src/webinar/core/registration.py`.
  - У шаблоні адаптер `src/app/adapters/turnstile/cloudflare.py` і змінні `TURNSTILE_*` є, але `create_app` (`src/app/main.py`) адаптер не будує, а скрипта й віджета немає.
  - Повертає зріз «реєстрація».

Прибрано також; чи повертати, вирішує v2:

- cookie `src` із джерелом переходу: UTM-позначки, `gclid`, `gbraid`, `wbraid`, сторінка входу, `Referer`. Cookie host-only, `HttpOnly`, 30 днів, значення — base64url від JSON (v1: `src/webinar/adapters/web/source.py`). З нього v1 заповнює поля `utm_*`, `gclid`, `gbraid`, `wbraid`, `landing_url`, `referrer`;
- приховане поле форми `ga_client_id`: його заповнює скрипт, коли аналітика активна (v1: `src/webinar/adapters/web/static/js/consent.js`, `syncClientId`; `src/webinar/core/registration.py`, `clean_ga_client_id`). З нього v1 заповнює поле `ga_client_id`.
