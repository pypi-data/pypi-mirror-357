# kos_Htools

Комплексная библиотека для работы с Telegram и Redis.

## Установка

```bash
pip install kos_Htools
```

## Компоненты

Библиотека включает два основных модуля:

### 1. Telethon Tools

Инструменты для работы с Telegram API:
- Поддержка множественных аккаунтов
- Парсинг пользователей из чатов и каналов
- Анализ сообщений
- Автоматическая работа с привязанными группами

### 2. Redis Tools

Инструменты для работы с Redis:
- Кэширование данных
- Сериализация/десериализация JSON
- Работа с ключами и значениями

## Настройка

1. Создайте файл `.env` в корневой директории вашего проекта
2. Добавьте следующие переменные:

```
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
TELEGRAM_PHONE_NUMBER=ваш_номер_телефона
```

Так же можно добавить proxy для каждой сессии например:
```
TELEGRAM_PROXY=socks5:ip:port:username:password 

Другой формат добавления:   
socks5:ip:port
http:ip:port
```

Для работы с несколькими аккаунтами, разделите значения через запятую:
```
TELEGRAM_API_ID=id1,id2,id3
TELEGRAM_API_HASH=hash1,hash2,hash3
TELEGRAM_PHONE_NUMBER=phone1,phone2,phone3
```

## Примеры использования

### Telegram Tools

```python
from kos_Htools.telethon_core import multi, create_custom_manager
from kos_Htools.telethon_core.utils.parse import UserParse
import asyncio

async def main():
    # Способ 1: Использование предварительно созданного экземпляра multi
    # (Использует данные из .env файла)
    client = await multi()
    
    # Способ 2: Создание пользовательского менеджера с собственными данными
    accounts_data = [
        {
            "api_id": 123456,
            "api_hash": "your_api_hash",
            "phone_number": "+1234567890",
            "proxy": None  # Можно указать прокси в формате tuple
        }
    ]
    custom_multi = create_custom_manager(
        accounts_data,
        system_version="Windows 10",  # Опционально
        device_model="PC 64bit"       # Опционально
    )
    custom_client = await custom_multi()

    # Парсинг пользователей
    parser = UserParse(client, {'chats': ['https://t.me/groupname']})
    user_ids = await parser.collect_user_ids()
    
    # Анализ сообщений пользователей
    messages = await parser.collect_user_messages(limit=100, sum_count=True)
    
    # Закрытие клиентов после использования
    await multi.stop_clients()
    await custom_multi.stop_clients()

if __name__ == '__main__':
    asyncio.run(main())
```

### Полный пример работы с парсингом пользователей

```python
from kos_Htools.telethon_core import multi
from kos_Htools.telethon_core.utils.parse import UserParse
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Получение клиента Telegram
    client = await multi()
    
    # Пример парсинга ID пользователей из чата
    chat_data = {'chats': ['https://t.me/example_chat']}
    parser = UserParse(client, chat_data)
    
    # Получение ID пользователей
    user_ids = await parser.collect_user_ids()
    if user_ids:
        logger.info(f"Собрано {sum(len(ids) for ids in user_ids.values())} ID пользователей")
        
    # Пример анализа сообщений пользователей
    messages = await parser.collect_user_messages(limit=200, sum_count=True)
    if messages:

        # Топ 5 активных пользователей
        top_users = sorted(
            messages.items(), 
            key=lambda x: x[1].get('total_messages', 0), 
            reverse=True
        )[:5]
        
        logger.info("Топ 5 активных пользователей:")
        for user_id, data in top_users:
            logger.info(f"Пользователь {user_id}: {data.get('total_messages', 0)} сообщений")
    
    # Закрытие клиентов
    await multi.stop_clients()
    
    return user_ids, messages

if __name__ == '__main__':
    asyncio.run(main())
```

### Redis Tools

#### RedisBase - Упрощенная работа с JSON данными

```python
from kos_Htools import RedisBase
import redis

# Создание Redis клиента
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Кэширование данных
redis_base = RedisBase(key="my_key", data={"example": "data"}, redis=redis_client)
redis_base.cached(ex=3600)  # ex - время жизни кэша в секундах

# Получение данных
cached_data = redis_base.get_cached()
```

#### RedisShortened - Специализированная работа со списками

> **Рекомендация:** Для работы со списками используйте `RedisShortened` вместо `RedisBase`

```python
from kos_Htools.redis_core.redisetup import RedisShortened
import redis

# Создание Redis клиента
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Работа со списками
redis_list = RedisShortened(key="my_list", data=[], redis=redis_client)

# Добавление элементов в начало списка
redis_list.lpush("item1", "item2", "item3")

# Добавление элементов в конец списка
redis_list.rpush("item4", "item5")

# Получение и удаление элемента с начала списка
first_item = redis_list.lpop()

# Получение и удаление элемента с конца списка
last_item = redis_list.rpop()

# Получение диапазона элементов (с 0 по 2)
items = redis_list.lrange(0, 2)

# Получение длины списка
length = redis_list.llen()
```

#### Описание методов RedisShortened

| Метод | Описание |
|-------|----------|
| `lpush(*values)` | Добавить элементы в начало списка |
| `rpush(*values)` | Добавить элементы в конец списка |
| `lpop()` | Получить и удалить элемент с начала списка |
| `rpop()` | Получить и удалить элемент с конца списка |
| `lrange(start, end)` | Получить диапазон элементов |
| `llen()` | Получить длину списка |
| `lrem()` | Удалить и проверить элемент в списке |

### SQLAlchemy DAO

В библиотеке реализован универсальный асинхронный слой доступа к данным (DAO) для работы с SQLAlchemy.

#### Пример использования

```python
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from my_models import User  # Ваша модель SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

dao = BaseDAO(User, db_session)  # db_session — экземпляр AsyncSession

# Получить одну запись по условию
user = await dao.get_one(User.user_id == 123456)

# Создать новую запись
new_user = await dao.create({'name': 'Иван', 'age': 30})

# Обновить запись
await dao.update(User.id == 1, {'name': 'Петр', 'age': 31})

# Получить все значения столбца
names = await dao.get_all_column_values(User.name)

# Получить все записи
all_users = await dao.get_all()
```

#### Описание методов BaseDAO

- **get_one(where)** — получить одну запись по условию (или None).
- **create(data)** — создать новую запись из словаря.
- **update(where, data)** — обновить запись по условию.
- **get_all_column_values(column)** — получить все значения столбца.
- **get_all()** — получить все записи модели.

## Требования

- Python 3.10+
- Telethon
- Redis
- SQLAlchemy
- python-dotenv 