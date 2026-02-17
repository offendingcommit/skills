# Yandex Tracker CLI Skill

Простой CLI для Yandex Tracker на чистом bash + curl. Работает напрямую через API с правильными заголовками (`X-Org-Id`). Не требует внешних зависимостей кроме `curl` и `jq`.

## Установка

1. Скопируйте скрипт в директорию в PATH:
```bash
mkdir -p ~/bin
cp yandex-tracker ~/bin/
chmod +x ~/bin/yandex-tracker
```

2. Создайте конфигурационный файл `~/.yandex-tracker-env`:
```bash
TOKEN= 'y0__...'      # OAuth токен из Tracker UI (Application → OAuth)
ORG_ID='7446...'     # On-premise Org ID (из URL или DevTools → X-Org-Id)
```

3. Убедитесь, что `jq` установлен:
```bash
sudo apt install jq   # Ubuntu/Debian
# или
brew install jq       # macOS
```

## Использование

### Основные команды

| Команда | Описание |
|---------|----------|
| `queues` | Список всех очередей (формат: `key<TAB>name`) |
| `queue-get <key>` | Детали очереди (JSON) |
| `queue-fields <key>` | Все поля очереди (включая локальные) |
| `issue-get <issue-id>` | Получить задачу (формат: `BIMLAB-123`) |
| `issue-create <queue> <summary>` | Создать задачу. Доп. поля через stdin (JSON) |
| `issue-update <issue-id>` | Обновить задачу (JSON через stdin) |
| `issue-delete <issue-id>` | Удалить задачу |
| `issue-comment <issue-id> <text>` | Добавить комментарий |
| `issue-transitions <issue-id>` | Возможные переходы статуса |
| `issue-close <issue-id> <resolution>` | Закрыть задачу (resolution: `fixed`, `wontFix`, `duplicate` и др.) |
| `issue-worklog <issue-id> <duration> [comment]` | Добавить worklog (duration: `PT1H30M`) |

### Примеры

```bash
# Список очередей
yandex-tracker queues

# Создать задачу с дополнительными полями
echo '{"priority":"critical","description":"Подробности"}' | yandex-tracker issue-create BIMLAB "Новая задача"

# Добавить комментарий
yandex-tracker issue-comment BIMLAB-266 "Работаю над этим"

# Добавить spent time
yandex-tracker issue-worklog BIMLAB-266 PT2H "Исследование"

# Получить возможные переходы (чтобы понять, как закрыть)
yandex-tracker issue-transitions BIMLAB-266 | jq .

# Обновить задачу (перевести в другую очередь, например)
echo '{"queue":"RAZRABOTKA"}' | yandex-tracker issue-update BIMLAB-266
```

## Примечания

- **Org-ID for on-premise:** Найдите в DevTools Tracker → Network → любой запрос → заголовок `X-Org-Id`.
- **Для Cloud Tracker** нужно изменить скрипт, заменив `X-Org-Id` на `X-Cloud-Org-Id`.
- Токен можно получить в Tracker UI: Settings → Applications → OAuth → Generate new token.
- Все команды выводят JSON через `jq` для удобной дальнейшей обработки.

## Структура

```
skills/yandex-tracker-cli/
├── yandex-tracker      # Исполняемый скрипт
├── SKILL.md            # Эта документация
└── .yandex-trackerrc   # (не в репо) Конфиг с TOKEN и ORG_ID
```

## Limitations

- Нет пагинации (т. первые 100 элементов)
- Нет продвинутого поиска (`issues_find` можно добавить)
- Простая валидация аргументов

## License

MIT
