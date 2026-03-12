# Karing — правила маршрутизации (RU-конфиг)

## Что это

`diversion_rules_custom.json` — кастомные правила diversion для прокси-клиента [Karing](https://github.com/KaringX/karing).
Логика: российские сайты → прямое соединение (`direct`), заблокированные → через VPN (`currentSelected`).

---

## Как применить на устройстве

### macOS
Рабочий конфиг лежит здесь:
```
~/Library/Group Containers/group.com.nebula.karing/karing_routing_group.json
```
Изменения в `diversion_rules_custom.json` нужно **вручную переносить** в этот файл (или импортировать через UI Karing).

### iOS / Android
В Karing: **Настройки → Маршрутизация → Импортировать** → вставить URL:
```
https://raw.githubusercontent.com/SmagArt/karing-rules/main/diversion_rules_custom.json
```
Файл универсальный — подходит для любого устройства с Karing. При импорте по URL правила обновляются автоматически при нажатии "Обновить" в приложении.

---

## Структура файла

```
rules[]
  ├── outbound: "block"         — блокировка (реклама, malware)
  ├── outbound: "direct"        — прямое соединение (Apple, RU-сайты)
  └── outbound: "currentSelected" — через выбранный VPN-сервер
```

Правила обрабатываются **сверху вниз** — первое совпадение выигрывает.

---

## Порядок правил (важен!)

| Приоритет | Правило | Действие |
|-----------|---------|----------|
| 1 | 🛑 Adblock / AdblockPlus | block |
| 2 | 🛑 malware / phishing | block |
| 3 | 🍎 Apple | direct |
| 4 | YouTube, Google, Instagram, Netflix, Discord, WhatsApp, Telegram, Claude, OpenAI | VPN |
| 5 | 🇷🇺 RU Domestic | direct |
| 6 | 🌏 GFW (заблокированные в РФ) | VPN |

> **Важно:** RU Domestic должен стоять **до** GFW, иначе российские IP попадут под VPN-правило.

---

## Что было исправлено / добавлено (март 2025)

### Исправлена опечатка
- `com.whatapp` → `com.whatsapp` (пакет WhatsApp не работал)

### ВКонтакте тормозил — добавлены CDN-домены
Весь медиаконтент ВК грузится с этих доменов, они шли через VPN:
- `userapi.com` — фото, видео, аватары (основной CDN)
- `vk-cdn.net` — статика
- `vkuservideo.net` — видео
- `vk-apps.com` — мини-приложения
- `vkplay.ru`, `vkplay.video` — VK Play

### Госуслуги не открывались — добавлена инфраструктура
- `goskey.ru` — Госключ (электронная подпись)
- `digital.gov.ru` — Минцифры (авторизация ЕСИА)
- `pfr.gov.ru` — Пенсионный фонд
- `sozrf.ru` — Социальный фонд России

### Банки детектили VPN — добавлены прямые домены
Приложения (ДОМРФ Банк / Генератор Слов, Озон Банк и др.) видели VPN, когда
часть их запросов шла через прокси. Добавлены в `direct`:
```
domrfbank.ru, domrf.ru, domclick.ru
ozonbank.ru
alfabank.ru, alfa-bank.ru
raiffeisen.ru
psbank.ru, rshb.ru
gazprombank.ru, gazprom.ru
rosbank.ru, pochtabank.ru
akbars.ru, sovcombank.ru
homecredit.ru, zenit.ru
mtsbank.ru, absolutbank.ru, vtb.com
```

---

## Как добавить новый сайт/приложение в прямое соединение

В секцию `🇷🇺 RU Domestic` в `domain_suffix`:
```json
"domain_suffix": [
  "example.ru",
  ...
]
```
`domain_suffix` покрывает домен и **все его поддомены** автоматически.

Для мобильного приложения дополнительно добавить `package`:
```json
"package": [
  "ru.example.app"
]
```

---

## Известные ограничения

- IDN-домены (кириллица, например `.рф`) в `domain_suffix` не поддерживаются — нужен punycode.
- `geosite:ru` покрывает большинство `.ru` доменов, но список неполный — поэтому критичные домены продублированы явно в `domain_suffix`.
- `geosite:category-bank-ru` — готовый набор всех российских банков от KaringX.
- `geosite:category-finance-ru` — финансовые сервисы (биржи, платёжки, страховые).
- Если приложение всё равно детектит VPN — скорее всего оно обращается к дополнительному домену (аналитика, API), который ещё не в списке. Найти через логи Karing (вкладка Connections).

---

## Диагностика проблем

1. **Сайт не открывается** — проверить вкладку **Connections** в Karing: к какому домену идёт запрос и через какое правило он маршрутизируется.
2. **Приложение видит VPN** — в Connections найти запросы от этого приложения, идущие через прокси, добавить их домены в `direct`.
3. **После правок** — перезапустить Karing (или переключить VPN off/on).
