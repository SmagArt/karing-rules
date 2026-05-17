# Karing — правила маршрутизации (RU-конфиг)

## Что это

`diversion_rules_custom.json` — кастомные правила diversion для [Karing](https://github.com/KaringX/karing).
Логика: РФ-сервисы → прямое соединение (`direct`), заблокированное в РФ → через
VPN (`currentSelected`), реклама и malware → блокировка (`block`).

---

## ⚠️ Главное: режим должен быть Rule

Правила применяются **только в режиме «Rule»** (по правилам). Если стоит
**«Global»** — весь трафик идёт через VPN, файл правил игнорируется целиком, и
РФ-приложения ловят детект VPN. **Это первое, что нужно проверять**, если
«всё настроено, а ВК/Маркет/WB всё равно видят VPN».

Зафиксировано 17.05.2026: именно из-за Global ломались VK/Маркет/WB на iPhone.

---

## Как применить на устройстве

### iOS / Android — импорт по URL

Karing → **Настройки → Маршрутизация → Импортировать** → URL:
```
https://raw.githubusercontent.com/SmagArt/karing-rules/main/diversion_rules_custom.json
```
Имя файла — **всегда через нижнее подчёркивание**: `diversion_rules_custom.json`.
После правок: запушить в репозиторий → в Karing нажать «Обновить».

### macOS

Рабочий конфиг: `~/Library/Group Containers/group.com.nebula.karing/karing_routing_group.json`.
Изменения переносить вручную или импортом через UI.

---

## Порты Karing (шестерёнка → Порт)

### Личный прокси (только это устройство)

| Порт | Режим | Что происходит |
|------|-------|----------------|
| **3067** | **Rule** ← рабочий, для Claude | Действуют все правила из `diversion_rules_custom.json` |
| 3065 | Direct | Всё напрямую, VPN отключён, правила игнорируются |
| 3066 | Global | Весь трафик через VPN, правила игнорируются |

### Раздача в LAN

| Порт | Режим |
|------|-------|
| 4067 | Rule, принимает подключения с других устройств |
| 4066 | Global, для раздачи |

### Служебные

| Порт | Назначение |
|------|-----------|
| 3057 | Синхронизация настроек Karing между устройствами |
| 3050 | Кластерный сервис |
| 3072 | Веб-панель управления в браузере |

Для ярлыка Claude — всегда порт **3067**.

---

## Структура файла

`rules[]` обрабатываются **сверху вниз**, первое совпадение выигрывает.

`outbound`: `block` — блокировка · `direct` — напрямую · `currentSelected` — через VPN.

Текущий порядок правил:

| # | Правило | Действие |
|---|---------|----------|
| 1 | Adblock / AdblockPlus / Malware & Phishing | block |
| 2 | Local Fitness API (Zepp/Huami) | direct |
| 3 | RU Marketplaces & CDN (WB/Ozon/Яндекс/Авито + их CDN) | direct |
| 4 | VK (app + Messenger + CDN) | direct |
| 5 | RU Priority (geosite/geoip:ru, банки, госуслуги, инфра) | direct |
| 6 | Xiaomi Home | direct |
| 7 | Apple (кроме рекламы) / Apple Ads | direct / block |
| 8 | YouTube, Gemini, Google, Instagram, Netflix, Discord, WhatsApp, Telegram, Claude, OpenAI, GitHub | currentSelected |
| 9 | GFW (заблокированное в РФ) | currentSelected |

**Важно:** все `direct`-правила РФ стоят **до** GFW, иначе российские IP уйдут под VPN.

---

## Почему РФ-приложения детектят VPN

Детект — по **IP выхода** (репутация подсети дата-центра). Если хоть один домен
приложения утечёт через VPN — сервис видит VPN-IP и блокирует. Лечится полнотой
`direct`-доменов: добавлять CDN, static, API-поддомены.

На **iOS** маршрутизация `package` (по приложению) **не работает** — нет per-app
без MDM. Спасают только `domain_suffix` и `geoip`.

---

## Как добавить сервис в direct

В `domain_suffix` нужного правила. `domain_suffix` покрывает домен и все
поддомены автоматически.

**Диагностика:** вкладка **Connections** в Karing → найти запрос приложения,
идущий через прокси (не direct) → добавить его домен в `direct`.

---

## Известные ограничения

- IDN-домены (`.рф`, кириллица) в `domain_suffix` не поддерживаются — нужен punycode.
- `geosite:ru` неполный — критичные домены продублированы явно.
- `process_name` — только desktop (Win/Linux/macOS); `package` — только Android.
  На iOS оба поля игнорируются.
- ECH/DoH: если приложение прячет домен, роутинг возможен только по `geoip:ru`.

---

## История изменений

- **2026-05** — добавлен блок `RU Marketplaces & CDN`: CDN маркетплейсов
  (`wbbasket.ru`, `wbstatic.net`, `wbx-content.ru`, `ozone.ru`, `yastatic.net`
  и др.), VK расширен (`mycdn.me`, `vkvideo.ru`, `vkuserlive.net`...).
  Урок: симптом «РФ-приложения видят VPN» был из-за режима **Global** вместо Rule.
- **2025-03** — Bitrix24, Xiaomi Home, банки РФ, `geosite:category-bank-ru`,
  CDN-домены ВК, инфраструктура Госуслуг.
