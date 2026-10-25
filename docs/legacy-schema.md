# Схема даних v1 і імпорт у v2

> **Приклад конкретного проєкту.** Схема даних першої версії сайту вебінару і перенесення її учасників у другу версію. Друга версія зібрана на цьому шаблоні: [agent.pythoncourse.me](https://agent.pythoncourse.me), код — [agent-webinar-efir](https://github.com/KonstZiv/agent-webinar-efir). Тут — версія 1 від 10.10.2026; пізніша — у репозиторії другої версії сайту (`docs/legacy-schema.md`). Новий проєкт видаляє або переписує цей документ разом із `docs/contract.md` і `tests/test_contract.py` (README, «Як почати проєкт»).

**Версія 1 · 10.10.2026.** Таблиці v1 — за міграцією `0001` (v1: `src/webinar/adapters/db/migrations/versions/0001_initial.py`; моделі — `src/webinar/adapters/db/models.py`; коміт `40b5de5`). Відповідність полів `participants` → `leads` — попередня: модель `leads` тут вихідна, остаточну задає v2. Решту домовленостей v1 і v2 описує `docs/contract.md`. Документ лежить в обох репозиторіях (`docs/legacy-schema.md`), копії однакові.

## Таблиці v1

Усі позначки часу — `timestamptz` в UTC. Ревізія Alembic — `0001` (таблиця `alembic_version`).

### `participants` — учасник

| Стовпець | Тип | NULL | Примітка |
| :-- | :-- | :-- | :-- |
| `id` | `bigint`, identity | ні | первинний ключ `pk_participants`; назовні не показується |
| `email` | `varchar(254)` | ні | `uq_participants_email`; CHECK `ck_participants_email_normalized`: `email = lower(email) AND email !~ '^\s\|\s$'` — без пробілів на краях, у нижньому регістрі |
| `unsubscribe_id` | `uuid` | ні | `uq_participants_unsubscribe_id`; основа токена відписки (`docs/contract.md`, розділ 4); застосунок генерує `uuid4` |
| `registered_at` | `timestamptz` | ні | час реєстрації за годинником застосунку |
| `consent_version` | `varchar(16)` | ні | завжди `consent-v1` (v1: `src/webinar/core/registration.py`, `CONSENT_VERSION`) |
| `consent_at` | `timestamptz` | ні | час згоди |
| `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` | `varchar(500)` | так | джерело переходу з cookie `src` |
| `gclid`, `gbraid`, `wbraid` | `varchar(500)` | так | ідентифікатори рекламного кліку Google |
| `landing_url`, `referrer` | `varchar(500)` | так | сторінка входу і сторінка, з якої перейшли |
| `ga_client_id` | `varchar(100)` | так | лише вигляду `<цифри>.<цифри>` і лише з активною аналітикою |

Позначки «відписаний» немає: відписка видаляє рядок, листи учасника видаляються каскадом.

### `emails` — лист учасникові

| Стовпець | Тип | NULL | Примітка |
| :-- | :-- | :-- | :-- |
| `id` | `bigint`, identity | ні | первинний ключ `pk_emails` |
| `participant_id` | `bigint` | ні | `fk_emails_participant_id_participants` → `participants.id`, `ON DELETE CASCADE` |
| `kind` | `varchar(32)` | ні | CHECK `ck_emails_kind`: `confirmation`, `reminder_day`, `reminder_hour`; UNIQUE `uq_emails_participant_id_kind` разом із `participant_id` |
| `status` | `varchar(16)` | ні | CHECK `ck_emails_status`: `pending`, `sent`, `failed` |
| `idempotency_key` | `uuid` | ні | `uq_emails_idempotency_key`; заголовок `Idempotency-Key` для Resend |
| `scheduled_at` | `timestamptz` | так | час відкладеного надсилання |
| `sent_at` | `timestamptz` | так | коли Resend прийняв лист |
| `resend_id` | `varchar(100)` | так | ідентифікатор листа в Resend |
| `last_error` | `varchar(500)` | так | статус і назва помилки, без персональних даних |
| `attempts` | `integer` | ні | за замовчуванням `0` (у базі й у моделі) |
| `created_at` | `timestamptz` | ні | за замовчуванням `now()` |
| `updated_at` | `timestamptz` | ні | за замовчуванням `now()`; оновлює ORM (`onupdate`), тригера в базі немає |

v1 створює лише листи `confirmation`: нагадування не реалізовано.

### Індекси

Окремих індексів міграція не створює. Є лише унікальні індекси, які PostgreSQL будує під первинні ключі й обмеження UNIQUE:

- `pk_participants` (`id`), `uq_participants_email` (`email`), `uq_participants_unsubscribe_id` (`unsubscribe_id`);
- `pk_emails` (`id`), `uq_emails_participant_id_kind` (`participant_id`, `kind`), `uq_emails_idempotency_key` (`idempotency_key`).

## Відповідність `participants` → `leads` (попередня)

| `participants` (v1) | `leads` (v2) | Примітка |
| :-- | :-- | :-- |
| — | `id` | v2 призначає сама; `participants.id` не переноситься |
| `email` | `email` | уже нормалізована (CHECK у v1); ключ злиття |
| `registered_at` | `created_at` | |
| — | `origin` | `v1` для кожного перенесеного запису |
| `consent_at` | `consent_at` | |
| `consent_version` | `consent_version` | `consent-v1` — текст згоди v1 (`docs/legal/consent.md` v1); правило — «Згода `consent-v1`» |
| `unsubscribe_id` | у вихідній моделі `leads` поля немає | значення має перейти без змін, інакше посилання відписки зі старих листів не працюватимуть (`docs/contract.md`, розділ 4); поле — рішення v2 |
| `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` | ті самі назви | у v1 — до 500 символів |
| `gclid`, `gbraid`, `wbraid` | ті самі назви | у v1 — до 500 символів |
| `ga_client_id` | `ga_client_id` | у v1 — до 100 символів |
| `landing_url`, `referrer` | ті самі назви | у v1 — до 500 символів |
| — | `email_status` | у v1 відповідника немає; значення для перенесених визначає v2 |
| — | `welcome_sent_at` | у `participants` відповідника немає; лист-підтвердження v1 — рядок `emails` з `kind = confirmation` і `sent_at`; чи вважати його привітанням, вирішує v2 |
| — | `level`, `extra` | у v1 немає; значення для перенесених визначає v2 |
| — | `ref_code`, `referred_by` | у v1 немає; значення для перенесених визначає v2 |
| — | `tg_user_id`, `tg_username`, `tg_linked_at`, `channel_member` | у v1 немає; значення для перенесених визначає v2 |

## Що не переноситься і чому

- **`emails`.** Це журнал поштового адаптера v1: ключі ідемпотентності Resend, `resend_id`, спроби, помилки. v2 надсилає листи власним адаптером із власним журналом, тож старі ключі і стани їй ні до чого.
- **`participants.id`.** Внутрішній ключ v1: назовні не показується, на нього посилаються лише `emails`. Записи зіставляє адреса.
- **Відписані учасники.** У v1 їх фізично немає: відписка видаляє рядок. Імпорт їх не відновлює.

## Злиття за email

- Ключ — нормалізована адреса: без пробілів на краях, у нижньому регістрі (v1: `src/webinar/core/email.py`, `normalize_email`; CHECK `ck_participants_email_normalized`). v2 нормалізує адреси так само, тоді однакові адреси збігаються.
- На одну адресу — один запис `leads`.
- Імпорт ідемпотентний: повторний запуск не створює дублів.
- Які значення перемагають для адреси, що вже є у v2, — рішення v2.

Остаточний імпорт (крок 4 порядку нижче) не повторює перший, а лише:

- видаляє з v2 перенесених лідів (`origin` = `v1`), адрес яких уже немає в `participants`: вони відписались у v1. Виняток — ті, хто за цей час реєструвався у v2: їхні записи лишаються (як це видно в `leads` — модель v2);
- додає учасників v1 із `registered_at` пізніше за момент, на який перший імпорт прочитав `participants`.

Лідів, яких v2 видалила відпискою, імпорт не відновлює: рядок у `participants` v1 лишається, але переноситься лише раз. Тест на це правило пише зріз v2 «імпорт».

Відписки з v2 у v1 не пересилаються. Нагадування v1 надсилаються до етапу 10 ефіру (`reminder_hour` — о 18:00 за Києвом), а після запуску v2 v1 листів не шле. Отже відписка, яку прийняла v2, не лишає за собою листів v1.

## Порядок імпорту і перемикання адрес

1. Перший імпорт завершено — одразу після деплою v2 на `agent`.
2. `agent.pythoncourse.me` обслуговує v2 — етап 10 ефіру 21.10.
3. Домен `agent-preparation.pythoncourse.me` переходить на сервіс v2 — після ефіру. До цього кроку v1 приймає відписки за `List-Unsubscribe` (`SERVICE_BASE_URL`) і нові реєстрації.
4. Остаточний імпорт — після кроку 3, коли v1 запитів уже не отримує.

**Відомий ризик.** Між деплоєм v2 і завершенням першого імпорту (хвилини в ефірі) відписка за посиланням з листа v1 показує «відписано», але нічого не видаляє: ліда у v2 ще немає. Потім перший імпорт додає цей запис. Це відкрите питання v2 (нижче).

## Згода `consent-v1`

`consent-v1` закріплено за текстом згоди v1 (`docs/legal/consent.md` v1, розділ «Текст позначки»). v2 зберігає копію цього тексту (наприклад, `docs/legal/archive/consent-v1.md`), а власні версії згоди називає інакше. Тоді в перенесених записів `consent_version` однозначно вказує, на який текст погодилась людина.

## Відкриті питання для v2

- Поле для `unsubscribe_id` у `leads`.
- Чи заповнювати `welcome_sent_at` з листа-підтвердження v1.
- Початкове `email_status` для перенесених записів.
- Пріоритет полів під час злиття, коли адреса є і у v1, і у v2.
- Відписки між деплоєм v2 і завершенням першого імпорту (відомий ризик вище).
