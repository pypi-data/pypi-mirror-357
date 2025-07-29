# API клиент пересказ YandexGPT

Асинхронный Python клиент для взаимодействия с API [пересказ YandexGPT](https://300.ya.ru/) с целью создания подробных или кратких пересказов статей или видео.

## Установка

Установите пакет используя pip:

```bash
pip install yandex-summary
```
Или Poetry:
```bash
poetry add yandex-summary
```
Или uv:
```bash
uv add yandex-summary
```

## Требования

- Python 3.8 или выше
- Действующий токен Yandex API (ключ можно получить [здесь](https://300.ya.ru/). Ключ задаётся с помощью переменной окружения `YANDEX_API_KEY` или в качестве параметра клиента)

## Использование

Вот пример использования библиотеки `yandex-summary` для получения пересказа статьи::

```python
import asyncio
from yandex_summary import YandexSummaryAPI

async def main():
    api = YandexSummaryAPI(api_key="ваш-апи-ключ-здесь")
    result = await api.get_summary(
        "https://example.com/article",
        summary_type="detailed",
    )
    if result.error:
        print(f"Ошибка: {result.error}")
    else:
        # Сохранить как обычный текст
        with open("summary.txt", mode="w", encoding="UTF-8") as file:
            file.write(result.to_plain_text())
        # Сохранить как Markdown
        with open("summary.md", mode="w", encoding="UTF-8") as file:
            file.write(result.to_markdown())
        # Сохранить как HTML
        with open("summary.html", mode="w", encoding="UTF-8") as file:
            file.write(result.to_html())

if __name__ == "__main__":
    asyncio.run(main())
```

## Функции

- Поддерживает как подробный, так и краткий пересказ.
- Выводит пересказ в виде обычного текста, Markdown или HTML.
- Обрабатывает повторные попытки и ошибки.

## Лицензия

Этот проект лицензирован по лицензии MIT. Подробности смотрите в файле [LICENSE](LICENSE).