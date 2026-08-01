# SRS-lite: требования к приложению Memo (на основе кода)

Дата анализа: 2026-03-16  
Режим анализа: статический анализ кода и миграций (без runtime-проверок)

## 1. Контекст и источники

Цель документа: зафиксировать требования в формате SRS-lite по текущей реализации (As-Is), отдельно показать расхождения с целевой схемой БД из запроса.

Ключевые источники:
- маршрутизация: `russian_memo/urls.py:13`, `account/urls.py:10`, `quiz/urls.py:11`, `words/urls.py:8`, `memorisation/urls.py:8`
- бизнес-логика аккаунтов: `account/views.py:56`, `account/views.py:94`, `account/views.py:140`, `account/views.py:387`, `account/views.py:444`
- роли и внешние идентичности: `account/models.py:5`, `account/models.py:23`, `account/models.py:33`, `account/models.py:42`
- тесты/квизы: `quiz/models.py:6`, `quiz/forms.py:12`, `quiz/views/teachers.py:17`, `quiz/views/students.py:16`
- колоды/карточки: `words/models.py:11`, `words/views.py:14`
- интервальные повторения и игры: `memorisation/models.py:8`, `memorisation/algorithm.py:1`, `memorisation/views.py:14`
- Telegram-бот: `bot/management/commands/runbot.py:15`, `bot/services/dictionary_service.py:3`, `bot/services/translation_service.py:3`
- конфигурация и эксплуатация: `russian_memo/settings.py:35`, `russian_memo/settings.py:97`, `Dockerfile:1`, `docker-compose.yml:1`, `.env.example:1`, `requirements.txt:1`

## 2. Карта системы (акторы и сценарии)

| Актор | Основные сценарии |
| --- | --- |
| Гость | Регистрация ученика/преподавателя, вход по логину/паролю, вход через VK, вход через Telegram |
| Ученик | Прохождение тестов, просмотр результатов, управление колодами и карточками, флешкарты (spaced repetition), игры |
| Преподаватель | Создание/редактирование/удаление тестов, работа с вопросами и ответами, просмотр результатов учеников |
| Администратор | Управление сущностями через Django Admin |
| Пользователь Telegram-бота | Команды `/define` и `/translate` |

Подсистемы:
- Web UI (Django templates + Materialize CSS)
- Учебный модуль тестов (`quiz`)
- Модуль карточек и повторений (`words`, `memorisation`)
- Социальная аутентификация (Telegram Login/WebApp, VK OAuth)
- Telegram-бот (командный интерфейс)

## 3. Публичные интерфейсы

### 3.1 HTTP интерфейсы

| Интерфейс | Метод | Актор | Назначение | Вход | Выход | Доступ |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | GET | Любой | Главная страница | - | HTML | Публично |
| `/admin/` | GET/POST | Администратор | Django Admin | Django admin формы | HTML | Требуется staff/superuser |
| `/account/login/` | GET/POST | Гость | Логин по username/password | `username`, `password` | Редирект + flash message | Публично |
| `/account/logout/` | GET | Авторизованный | Выход из сессии | - | Редирект | Нужна сессия |
| `/account/dashboard/` | GET | Авторизованный | Личный кабинет | - | HTML | `login_required` |
| `/account/student_registration/` | GET/POST | Гость | Регистрация ученика | поля `UserCreationForm` | HTML/редирект | Публично |
| `/account/teacher_registration/` | GET/POST | Гость | Регистрация преподавателя | поля `UserCreationForm` | HTML/редирект | Публично |
| `/account/telegram_auth/` | GET/POST | Гость | Вход через Telegram Login Widget | Telegram payload | Редирект | `csrf_exempt`, подпись проверяется |
| `/account/telegram_webapp_auth/` | POST | Mini App | Вход через Telegram WebApp | `init_data` | JSON `{ok, redirect/error}` | `csrf_exempt`, подпись проверяется |
| `/account/tg_auth/` | GET | Mini App | Bootstrap-страница WebApp-авторизации | - | HTML+JS | Публично |
| `/account/vk_oauth_start/` | GET | Гость | Старт VK OAuth | `next?` | Редирект на VK | Публично |
| `/account/vk_oauth_callback/` | GET | VK OAuth | Callback VK OAuth | `code`, `state` | Редирект + flash message | Публично, state проверяется |
| `/quiz/` | GET | Преподаватель | Список тестов преподавателя | - | HTML | `login_required` + teacher decorator |
| `/quiz/add/` | GET/POST | Преподаватель | Создание теста | `name` | Редирект | `login_required` + teacher decorator |
| `/quiz/<pk>/` | GET/POST | Преподаватель | Редактирование теста | `name` | HTML/редирект | `login_required` + teacher decorator |
| `/quiz/<pk>/delete/` | GET/POST | Преподаватель | Удаление теста | - | Редирект | `login_required` + teacher decorator |
| `/quiz/<pk>/results/` | GET | Преподаватель | Результаты теста | - | HTML | `login_required` + teacher decorator |
| `/quiz/<pk>/question/add/` | GET/POST | Преподаватель | Добавить вопрос | `text` | Редирект | `login_required` + teacher decorator |
| `/quiz/<quiz_pk>/question/<question_pk>/` | GET/POST | Преподаватель | Редактировать вопрос и ответы | `text`, formset answers | HTML/редирект | `login_required` + teacher decorator |
| `/quiz/<quiz_pk>/question/<question_pk>/delete` | GET/POST | Преподаватель | Удалить вопрос | - | Редирект | `login_required` + teacher decorator |
| `/quiz/list/` | GET | Ученик | Список доступных тестов | - | HTML | `login_required` + student decorator |
| `/quiz/take_quiz/<pk>/` | GET/POST | Ученик | Прохождение теста | выбранный ответ | HTML/редирект | `login_required` + student decorator |
| `/quiz/taken/` | GET | Ученик | История попыток | - | HTML | `login_required` + student decorator |
| `/quiz/<pk>/studentresults/` | GET | Ученик | Детальный результат | - | HTML | `login_required` + student decorator |
| `/words/decks/add/` | GET/POST | Ученик | Создание колоды | `title`, `color` | HTML/редирект | `login_required` + student decorator |
| `/words/decks/` | GET | Ученик | Список колод | - | HTML | `login_required` + student decorator |
| `/words/<pk>/cards/` | GET | Ученик | Карточки колоды | - | HTML | `login_required` + student decorator |
| `/words/<pk>/cards/add/` | GET/POST | Ученик | Создание карточки | `word`, `explanation`, `translation`, `synonymes` | HTML/редирект | Только `login_required` |
| `/words/decks/<pk>/` | GET/POST | Ученик | Редактирование колоды | `title`, `color` | HTML/редирект | `login_required` + student decorator |
| `/words/cards/<pk>/` | GET/POST | Ученик | Редактирование карточки | поля карточки | HTML/редирект | `login_required` + student decorator |
| `/words/cards/<pk>/delete/` | GET/POST | Ученик | Удаление карточки | - | HTML/редирект | `login_required` + student decorator |
| `/words/decks/<pk>/delete/` | GET/POST | Ученик | Удаление колоды | - | HTML/редирект | `login_required` + student decorator |
| `/games/flashcards/` | GET | Ученик | Следующая карточка к повторению | - | HTML | `login_required` |
| `/games/process_rating/` | POST | Ученик | Принять рейтинг карточки | `id`, `rating` | Редирект | `post_required` + `login_required` |
| `/games/hangman/` | GET | Ученик | Игра “Виселица” | - | HTML+JS | `login_required` + student decorator |
| `/games/translate/` | GET | Ученик | Игра “Скоростной набор” | - | HTML+JS | `login_required` + student decorator |
| `/api/users/<username>/cards/` | GET | JS-клиент игр | JSON карточек пользователя | `username` в URL | JSON | `login_required`, без role-check |

Трассировка: `russian_memo/urls.py:13`, `account/urls.py:10`, `quiz/urls.py:11`, `words/urls.py:8`, `memorisation/urls.py:8`, `words/views.py:147`

### 3.2 Команды Telegram-бота

| Команда | Актор | Назначение | Вход | Выход |
| --- | --- | --- | --- | --- |
| `/define <word>` | Пользователь бота | Получить словарное определение | слово | MarkdownV2 ответ с частями речи/примерами/синонимами |
| `/translate <text>` | Пользователь бота | Перевод EN->RU | текст | Строка `#translation` + перевод |

Трассировка: `bot/management/commands/runbot.py:50`, `bot/management/commands/runbot.py:61`, `bot/services/dictionary_service.py:7`, `bot/services/translation_service.py:7`

## 4. Функциональные требования (FR)

Формат: `ID | Актор | Условие | Ожидаемое поведение | Ограничения | Критерий приемки | Трассировка`.

| ID | Актор | Условие | Ожидаемое поведение | Ограничения | Критерий приемки | Трассировка |
| --- | --- | --- | --- | --- | --- | --- |
| FR-001 | Гость | Открыта регистрация ученика | Система создает пользователя и назначает роль `student` | Форма `UserCreationForm` | После submit пользователь авторизован и попадает на главную | `account/forms.py:24`, `account/views.py:56` |
| FR-002 | Гость | Открыта регистрация преподавателя | Система создает пользователя и назначает роль `teacher` | Форма `UserCreationForm` | После submit пользователь авторизован и попадает на главную | `account/forms.py:8`, `account/views.py:79` |
| FR-003 | Гость | Введены username/password | Выполняется аутентификация и вход в сессию | Нужна существующая учетная запись | При валидных данных создается сессия и выполняется редирект по роли | `account/views.py:94` |
| FR-004 | Авторизованный | Нажата кнопка выхода | Сессия завершается | - | После запроса `/account/logout/` пользователь разлогинен | `account/views.py:129` |
| FR-005 | Гость | Настроен VK OAuth | На login/signup страницах доступна кнопка VK | Требуются `VK_APP_ID` и `VK_APP_SECRET` | Кнопка “Войти через VK” отображается только при корректной конфигурации | `account/views.py:33`, `templates/account/login.html:47`, `templates/account/student_signup.html:79` |
| FR-006 | Гость | Настроен Telegram bot | На странице регистрации ученика отображается Telegram Login Widget | Требуется `TELEGRAM_BOT_NAME` | Виджет отображается и отправляет callback в backend | `account/views.py:61`, `templates/account/student_signup.html:66` |
| FR-007 | Гость | Telegram прислал login payload | Система валидирует подпись, создает/находит student и логинит | Только для роли student | При валидных данных происходит редирект на список тестов ученика | `account/views.py:140`, `account/views.py:342`, `account/views.py:387` |
| FR-008 | Mini App пользователь | Отправлен `init_data` | Система валидирует Telegram initData и возвращает JSON c redirect | Только POST | Ответ `{ok:true, redirect:...}` при успехе, `{ok:false,error}` при ошибке | `account/views.py:176`, `account/views.py:417`, `templates/account/telegram_mini_app_auth.html:26` |
| FR-009 | Гость | Запущен VK OAuth flow | Система выполняет stateful OAuth, создает/находит student по внешней идентичности и логинит | Только student через VK | Успешный callback логинит пользователя и делает safe redirect | `account/views.py:444`, `account/views.py:468`, `account/views.py:534` |
| FR-010 | Ученик | Открыт список тестов | Показываются только тесты с вопросами, которые еще не завершены пользователем | Учитываются завершенные попытки | В списке нет пройденных тестов и пустых тестов | `quiz/views/students.py:23` |
| FR-011 | Ученик | Старт теста | Создается или продолжается незавершенная попытка `QuizAttempt` | Один активный attempt на тест | При первом заходе создается attempt c `score=0, percentage=0` | `quiz/views/students.py:87` |
| FR-012 | Ученик | Отправлен ответ на текущий вопрос | Ответ сохраняется, прогресс двигается на следующий вопрос | Ответ обязателен | После последнего вопроса attempt закрывается и вычисляется процент | `quiz/forms.py:27`, `quiz/views/students.py:134` |
| FR-013 | Ученик | Тест уже завершен ранее | Повторное прохождение блокируется | Проверка по `finished_at` | При повторном запуске редирект в историю пройденных тестов | `quiz/views/students.py:79` |
| FR-014 | Ученик | Открыта страница истории | Показываются завершенные попытки пользователя | - | Список отсортирован по времени завершения | `quiz/views/students.py:35` |
| FR-015 | Ученик | Открыт детальный результат теста | Отображаются вопросы и итоговый процент по последней попытке | Должна быть завершенная попытка | Есть progress/result view по конкретному тесту | `quiz/views/students.py:48`, `templates/quiz/students/quiz_result.html:1` |
| FR-016 | Ученик | Отправлена форма колоды | Создается колода пользователя | Требуются `title`, `color` | Новая колода видна в списке | `words/views.py:14`, `words/models.py:11` |
| FR-017 | Ученик | Открыт список колод | Выдаются колоды текущего пользователя | Фильтр по owner | Пользователь видит только свои колоды | `words/views.py:35` |
| FR-018 | Ученик | Создана карточка в колоде | Создается `Card`, автоматически инициализируется запись практики | Привязка к deck | После создания есть `Practice` со стартовыми параметрами | `words/views.py:61`, `words/models.py:41` |
| FR-019 | Ученик | Редактирование/удаление карточек и колод | Система позволяет update/delete сущностей | Требуется авторизация | После submit данные изменены/удалены и показано уведомление | `words/views.py:72`, `words/views.py:87`, `words/views.py:103`, `words/views.py:125` |
| FR-020 | Ученик | Открыты флешкарты | Система выбирает ближайшую просроченную карточку к повторению | Сортировка по due | Если карточек нет, показывается дата следующего повторения | `memorisation/views.py:15` |
| FR-021 | Ученик | Отправлен рейтинг карточки | Пересчитывается следующий due по алгоритму SuperMemo-подобного интервала | Только POST | После submit карточка получает новый due/reps/ease_factor | `memorisation/views.py:43`, `memorisation/models.py:27`, `memorisation/algorithm.py:1` |
| FR-022 | Ученик | Запущены игры | Доступны экраны “Виселица” и “Скоростной набор” | Нужна авторизация | Страницы игр открываются и загружают JS-логику | `memorisation/views.py:64`, `memorisation/views.py:70`, `memorisation/urls.py:9` |
| FR-023 | JS-клиент игр | Запрошен `/api/users/<username>/cards/` | API возвращает JSON-сериализацию карточек | Требуется сессия пользователя | Ответ имеет `content_type=application/json` | `russian_memo/urls.py:21`, `words/views.py:147` |
| FR-024 | Преподаватель | Создание теста | Создается тест с owner=current user | Только teacher | После сохранения redirect на добавление вопроса | `quiz/views/teachers.py:18` |
| FR-025 | Преподаватель | Редактирование теста | Можно изменить название и просмотреть список вопросов | Только owner | Обновление теста сохраняется без смены owner | `quiz/views/teachers.py:46` |
| FR-026 | Преподаватель | Добавление вопроса | Вопрос привязывается к конкретному тесту owner-а | Только owner | Новый вопрос создается и открывается экран ответов | `quiz/views/teachers.py:141` |
| FR-027 | Преподаватель | Редактирование вопроса и ответов | Сохраняются текст вопроса и набор ответов (min 2, max 10) | Нужен минимум 1 правильный ответ | Невалидный formset не сохраняется, валидный сохраняется транзакционно | `quiz/forms.py:12`, `quiz/views/teachers.py:168` |
| FR-028 | Преподаватель | Удаление теста/вопроса | Система удаляет сущность и показывает confirmation flow | Только owner | После удаления происходит редирект в релевантный список | `quiz/views/teachers.py:70`, `quiz/views/teachers.py:87` |
| FR-029 | Преподаватель | Просмотр результатов теста | Отображаются попытки учеников, средний балл, число участников | Только owner | Видны только завершенные попытки (`finished_at is not null`) | `quiz/views/teachers.py:113` |
| FR-030 | Администратор | Работа в Django Admin | Доступны CRUD-операции по основным моделям | Нужны права admin | Модели account/quiz/words/memorisation зарегистрированы в admin | `account/admin.py:6`, `quiz/admin.py:5`, `words/admin.py:6`, `memorisation/admin.py:6` |
| FR-031 | Пользователь Telegram-бота | Команда `/define` | Бот отправляет определение слова (MarkdownV2) | Нужен аргумент слова | При длинном ответе бот отправляет несколько сообщений | `bot/management/commands/runbot.py:50`, `bot/services/dictionary_service.py:7` |
| FR-032 | Пользователь Telegram-бота | Команда `/translate` | Бот переводит текст EN->RU | Нужен аргумент текста | Бот возвращает перевод или текст ошибки | `bot/management/commands/runbot.py:61`, `bot/services/translation_service.py:7` |

## 5. Нефункциональные требования (NFR)

Формат: `ID | Категория | Требование | Критерий приемки | Статус As-Is | Трассировка`.

| ID | Категория | Требование | Критерий приемки | Статус As-Is | Трассировка |
| --- | --- | --- | --- | --- | --- |
| NFR-SEC-001 | Безопасность | Пароли пользователей хранятся через стандартные механизмы Django auth | В системе нет plaintext-паролей; аутентификация через `auth.authenticate` | Частично реализовано | `account/forms.py:8`, `account/views.py:99`, `russian_memo/settings.py:125` |
| NFR-SEC-002 | Безопасность | Ролевая авторизация для student/teacher через декораторы | Закрытые endpoint недоступны неавторизованным/неролевым пользователям | Частично, есть критический дефект (см. Risk R-001) | `account/decorators.py:16`, `quiz/views/teachers.py:17`, `quiz/views/students.py:16` |
| NFR-SEC-003 | Безопасность | Вход Telegram Widget защищен криптоподписью и TTL | Невалидная подпись/просрочка не допускаются | Реализовано | `account/views.py:140` |
| NFR-SEC-004 | Безопасность | Вход Telegram WebApp проверяет initData подпись | На неверных данных API возвращает 400 с ошибкой | Реализовано | `account/views.py:176`, `account/views.py:423` |
| NFR-SEC-005 | Безопасность | VK OAuth защищен state и safe-next redirect | Несовпадение state отклоняется; next редирект только на allowed host | Реализовано | `account/views.py:473`, `account/views.py:534` |
| NFR-SEC-006 | Безопасность | Стандартные формы защищены CSRF | POST формы содержат `{% csrf_token %}` | Реализовано | `templates/account/login.html:28`, `templates/words/deck_add.html:11`, `templates/quiz/add_quiz.html:14` |
| NFR-SEC-007 | Безопасность | Исключения CSRF должны быть минимально необходимыми и компенсированы проверками | Telegram endpoint имеют `csrf_exempt` и альтернативную криптопроверку payload | Реализовано с компенсирующими мерами | `account/views.py:387`, `account/views.py:416` |
| NFR-SEC-008 | Безопасность | Прод-настройки не должны использовать DEBUG и хардкод секретов | `DEBUG=False`, `SECRET_KEY` вне репозитория | Не выполнено (Gap) | `russian_memo/settings.py:23`, `russian_memo/settings.py:26` |
| NFR-REL-001 | Надежность | Критичные multi-step записи выполняются атомарно | При ошибке промежуточные изменения не коммитятся | Реализовано для signup/question update | `account/forms.py:14`, `quiz/views/teachers.py:183` |
| NFR-REL-002 | Надежность | Внешний словарный API должен деградировать без падения процесса | При timeout/HTTP error возвращается корректный fallback (`None`) | Реализовано | `bot/adapters/dictionary_client/client.py:32` |
| NFR-REL-003 | Надежность | Сервис перевода должен обрабатывать сбои провайдера | При ошибке возвращается пользовательское сообщение | Реализовано | `bot/services/translation_service.py:10` |
| NFR-REL-004 | Надежность | Логика квиза должна завершать attempt детерминированно | После ответа на последний вопрос фиксируются `score`, `percentage`, `finished_at` | Реализовано | `quiz/views/students.py:107`, `quiz/views/students.py:156` |
| NFR-REL-005 | Надежность | Поведение при ошибках входа должно быть явным для пользователя | Ошибки аутентификации выводятся через messages и редиректы | Реализовано | `account/views.py:113`, `account/views.py:498` |
| NFR-REL-006 | Надежность | Должно быть автоматизированное тестовое покрытие критичных потоков | Набор unit/integration тестов в репозитории | Не выполнено (Gap) | `account/tests.py:1`, `quiz/tests.py:1`, `words/tests.py:1`, `memorisation/tests.py:1` |
| NFR-PERF-001 | Производительность | Списки должны использовать фильтрацию/агрегацию на уровне БД | Используются `annotate`, `Count`, `order_by`, `exclude` | Реализовано | `quiz/views/students.py:25`, `quiz/views/teachers.py:40` |
| NFR-PERF-002 | Производительность | Аналитические экраны используют оптимизированные связи | Для teacher results применяется `select_related('student')` | Реализовано | `quiz/views/teachers.py:120` |
| NFR-PERF-003 | Производительность | Бот должен учитывать лимиты длины сообщений Telegram | Сообщения режутся на чанки до 3500 символов | Реализовано | `bot/management/commands/runbot.py:22` |
| NFR-PERF-004 | Производительность | API/списки должны поддерживать масштабирование (пагинация/кэш) | Наличие пагинации/кэша на больших выборках | Не выполнено (Gap) | `words/views.py:35`, `quiz/views/students.py:23` |
| NFR-OPS-001 | Эксплуатация | Поддержка локального и контейнерного запуска | Dockerfile + compose + local manage.py workflow | Реализовано | `Dockerfile:1`, `docker-compose.yml:1`, `README.md:1` |
| NFR-OPS-002 | Эксплуатация | БД должна переключаться SQLite/PostgreSQL по окружению | При `POSTGRES_DB` используется Postgres, иначе SQLite | Реализовано | `russian_memo/settings.py:97` |
| NFR-OPS-003 | Эксплуатация | Интеграции управляются через env-переменные | Все ключи Telegram/VK/Yandex заданы через env | Реализовано | `russian_memo/settings.py:227`, `.env.example:1` |
| NFR-OPS-004 | Эксплуатация | Таймзона и локаль должны быть заданы явно | RU locale + UTC timezone + USE_TZ | Реализовано | `russian_memo/settings.py:157`, `russian_memo/settings.py:160`, `russian_memo/settings.py:166` |
| NFR-OPS-005 | Эксплуатация | Требуемые зависимости должны быть зафиксированы в requirements | Наличие используемых библиотек в `requirements.txt` | Частично, отсутствуют пакеты для бота (см. R-007) | `requirements.txt:1`, `bot/management/commands/runbot.py:5`, `bot/adapters/translation_cient.py:4` |
| NFR-MNT-001 | Поддерживаемость | Схема БД должна быть консистентной между кодом и целевой моделью данных | Расхождения документированы и приоритезированы | Частично, есть drift | `account/models.py:5`, `quiz/models.py:6`, `words/models.py:11`, `memorisation/models.py:8` |
| NFR-MNT-002 | Поддерживаемость | Бизнес-правила ролей должны быть однозначными и не двусмысленными в коде | Проверки роли используют корректные bool-значения | Не выполнено (Gap, R-001) | `account/models.py:16`, `account/decorators.py:22`, `account/views.py:106` |
| NFR-MNT-003 | Поддерживаемость | Технический долг должен быть отслеживаемым | TODO и невалидные ссылки явно зафиксированы | Частично | `templates/quiz/quiz_update.html:34`, `russian_memo/assets/js/hangman.js:1`, `russian_memo/assets/js/speed_typing.js:1` |

## 6. Матрица “Код vs целевая схема БД”

Обозначения статуса:
- `OK`: совпадает или практически совпадает
- `PARTIAL`: совпадает частично, есть важные отличия
- `MISMATCH`: существенное расхождение

| Таблица из целевой схемы | Ожидается (из запроса) | Фактическое поведение в коде | Статус | Комментарий/влияние | Трассировка |
| --- | --- | --- | --- | --- | --- |
| `users` | PK BIGINT + поля auth + `deleted_at` | Таблица `users` от `AbstractUser`, PK AutoField, есть доп. поля `username`, `last_login`, `groups`, `user_permissions` | PARTIAL | Логически совместимо, но тип PK и состав полей отличаются | `account/models.py:5` |
| `roles` | `id`, `name UNIQUE` | Полное совпадение по смыслу | OK | - | `account/models.py:23` |
| `user_roles` | Composite PK (`role_id`,`user_id`) | Есть отдельный `id` + `unique_together(user, role)` | PARTIAL | Кардинальность совпадает, ключевая стратегия другая | `account/models.py:33` |
| `decks` | `title`, `color`, `user_id`, `created_at`, `deleted_at` | `title` сделан `unique` и nullable, связь `student -> users` | PARTIAL | Ограничение уникальности `title` может конфликтовать с ожиданием | `words/models.py:11` |
| `cards` | `word`, `explanation`, `translation`, `synonymes`, `deck_id`, timestamps | Практически совпадает | OK | - | `words/models.py:25` |
| `card_practices` | Таблица во множественном числе | В коде `card_practice` (singular) | MISMATCH | Нейминг отличается, может ломать внешние отчеты/SQL | `memorisation/models.py:20` |
| `card_reviews` | `practice_id -> card_practices`, `rating`, `reviewed_at` | `card_reviews` + FK на `card_practice` | PARTIAL | Семантика совпадает, но ссылка на таблицу с другим именем | `memorisation/models.py:37` |
| `quizzes` | `name UNIQUE`, `owner_id`, `created_at` | `name` не unique, есть доп. `deleted_at` | PARTIAL | Уникальность имени не enforced; soft-delete добавлен сверх схемы | `quiz/models.py:6` |
| `questions` | `text`, `position`, `quiz_id`, `deleted_at` | По сути совпадает | OK | Позиция автоинкрементируется внутри quiz | `quiz/models.py:20` |
| `answers` | В целевой таблице указаны `text/position/quiz_id` | В коде `text`, `is_correct`, `question_id`, `deleted_at` | MISMATCH | Структуры существенно различаются; вероятно, целевая схема содержит ошибку/устаревший вариант | `quiz/models.py:40` |
| `quiz_attempts` | `quiz_id`, `student_id`, `started_at`, `finished_at`, `score`, `percentage` | Полное совпадение по смыслу | OK | - | `quiz/models.py:53` |
| `selected_answers` | `attempt_id`, `selected_answer_id nullable`, `answered_at` | Совпадает | OK | - | `quiz/models.py:68` |
| `external_identities` | `provider_user_id UNIQUE`, метаданные профиля | В коде уникальность составная `(provider, provider_user_id)` | PARTIAL | Поддержка нескольких провайдеров для одинакового ID улучшает гибкость, но отличается от схемы | `account/models.py:42` |

Дополнительное глобальное расхождение:
- в целевой схеме PK помечены как `BIGINT`, в коде Django 3.0 по умолчанию используется `AutoField` (int)  
Трассировка: модели во всех app (`account/models.py:5`, `quiz/models.py:6`, `words/models.py:11`, `memorisation/models.py:8`).

## 7. Gaps & Risks (приоритизация)

| ID | Приоритет | Влияние | Риск/разрыв | Доказательство |
| --- | --- | --- | --- | --- |
| R-001 | HIGH | Безопасность доступа | Проверки роли используют методы как свойства (`u.is_student`, `u.is_teacher`) и становятся truthy по факту существования bound method | `account/models.py:16`, `account/decorators.py:22`, `account/decorators.py:37`, `account/views.py:106` |
| R-002 | HIGH | Защита данных | В `words` часть операций не ограничена владельцем объекта (доступ по чужому `pk`) | `words/views.py:65`, `words/views.py:95`, `words/views.py:117`, `words/views.py:139` |
| R-003 | HIGH | Доступность игр/API | API карточек использует некорректный relation path `deck__student__user__username` (вероятный runtime error) | `words/views.py:149` |
| R-004 | MEDIUM | Функциональность | Редирект на несуществующий route `quiz:dashboard` при отсутствии попытки | `quiz/views/students.py:61`, `quiz/urls.py:11` |
| R-005 | HIGH | Безопасность прод-окружения | `DEBUG=True` и хардкод `SECRET_KEY` в settings | `russian_memo/settings.py:23`, `russian_memo/settings.py:26` |
| R-006 | MEDIUM | Надежность релизов | Отсутствуют автотесты критичных сценариев | `account/tests.py:1`, `quiz/tests.py:1`, `words/tests.py:1`, `memorisation/tests.py:1` |
| R-007 | MEDIUM | Эксплуатация бота | В `requirements.txt` отсутствуют явно используемые зависимости `requests` и Telegram SDK | `requirements.txt:1`, `bot/adapters/translation_cient.py:4`, `bot/management/commands/runbot.py:5` |
| R-008 | MEDIUM | Эксплуатация/переносимость | JS игр содержит hardcoded ngrok host и fallback username | `russian_memo/assets/js/hangman.js:2`, `russian_memo/assets/js/speed_typing.js:2`, `russian_memo/assets/js/speed_typing.js:5` |
| R-009 | LOW | Поддерживаемость UI | В шаблонах есть TODO и нерабочие delete-link заглушки | `templates/quiz/quiz_update.html:34` |
| R-010 | MEDIUM | Консистентность данных | В коде присутствуют поля `deleted_at`, но удаления выполняются физически через `DeleteView` | `words/views.py:114`, `words/views.py:136`, `quiz/views/teachers.py:80` |

## 8. Проверка качества результата

Проверка по критериям из плана:
- Каждое FR и NFR содержит трассировку к конкретным исходникам.
- Интерфейсы перечислены для `/account/*`, `/quiz/*`, `/words/*`, `/games/*`, `/api/users/<username>/cards/`, а также команд Telegram-бота.
- Явно разделены `фактическое поведение (As-Is)` и `ожидания по целевой схеме` в матрице раздела 6.
- Отдельно выделены риски с приоритетами и влиянием (раздел 7).

Ограничения анализа:
- Django-окружение в текущей сессии не активировано, поэтому не выполнялись runtime-проверки маршрутов/ORM и миграций.
- Документ построен по коду, шаблонам, миграциям и конфигурации репозитория.
