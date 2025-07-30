import asyncio                          # Импорт модуля для работы с асинхронным программированием
import aiosqlite                        # Импорт библиотеки для асинхронной работы с SQLite
import logging                          # Импорт модуля логгирования
from typing import Optional            # Импорт типа Optional для аннотаций
from datetime import datetime, timedelta  # Импорт классов datetime и timedelta для работы со временем

# Настраиваем логгер
logger = logging.getLogger("ShortMemory")  # Создаём логгер с именем класса
logger.setLevel(logging.DEBUG)             # Уровень логирования — DEBUG
handler = logging.StreamHandler()          # Обработчик вывода в консоль
formatter = logging.Formatter('[%(name)s][%(funcName)s] %(message)s')  # Формат логов
handler.setFormatter(formatter)
logger.addHandler(handler)

# Класс кратковременной памяти. Хранит пары сообщений user/agent в SQLite.
class ShortMemory:
    def __init__(
        self,
        db_path: str = "short_memory.db",              # Путь к SQLite-файлу
        max_pairs: int = 10,                           # Максимум пар user/agent в истории
        ttl_minutes: int = 60,                         # Время хранения записей, мин
        cleanup_interval_minutes: int = 5,             # Частота автоочистки (если активирована)
        start_auto_cleanup: bool = True,               # Флаг автоочистки (не используется здесь)
    ):
        self.db_path = db_path                         # Сохраняем путь к базе данных
        self.max_pairs = max_pairs                     # Сохраняем лимит пар сообщений
        self.ttl_minutes = ttl_minutes                 # Сохраняем время жизни сообщений
        self.cleanup_interval_minutes = cleanup_interval_minutes  # Частота очистки
        self.start_auto_cleanup = start_auto_cleanup   # Флаг автоочистки (резерв, не используется)
        self._db: Optional[aiosqlite.Connection] = None  # Переменная для подключения к БД
        self._initialization_lock = asyncio.Lock()     # Блокировка, чтобы не было повторной инициализации
        logger.debug(f"Инициализирован с db_path={db_path}, max_pairs={max_pairs}, ttl_minutes={ttl_minutes}, cleanup_interval_minutes={cleanup_interval_minutes}, start_auto_cleanup={start_auto_cleanup}")

    # Унифицированный логгер исключений
    def _log_exception(self, message: str, exc: Exception):
        logger.error(f"{message}: {type(exc).__name__} - {exc}")

    # Инициализация базы данных (создание таблицы и индекса)
    async def init(self):
        logger.debug("Вход в init()")
        async with self._initialization_lock:          # Гарантируем, что инициализация не будет повторной
            if self._db:                               # Если уже инициализировано — выходим
                logger.debug("Подключение к БД уже существует, выходим из init")
                return
            try:
                self._db = await aiosqlite.connect(self.db_path)  # Подключение к БД
                logger.debug("Успешное подключение к БД")
                await self._db.execute("""                        # Создание таблицы, если не существует
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY,
                        user_id TEXT,
                        agent_id TEXT,
                        message TEXT,
                        role TEXT,
                        timestamp TEXT
                    )
                """)
                logger.debug("Таблица memory создана или уже существует")
                await self._db.execute("""                        # Создание индекса по user_id, agent_id и времени
                    CREATE INDEX IF NOT EXISTS idx_user_agent_timestamp
                    ON memory (user_id, agent_id, timestamp)
                """)
                logger.debug("Индекс создан или уже существует")
                await self._db.commit()                           # Сохраняем изменения
                logger.debug("Коммит после инициализации выполнен")
            except Exception as e:
                self._log_exception("init failed", e)            # Логируем ошибку
                self._db = None                                   # Обнуляем БД, если инициализация не удалась

    # Проверка и восстановление подключения к БД при необходимости
    async def _ensure_db(self):
        logger.debug("Проверка подключения к БД")
        if self._db is None:                  # Если подключения нет
            await self.init()                 # Пытаемся инициализировать
        if self._db is None:                  # Если не получилось — выбрасываем ошибку
            logger.error("Подключение к базе данных не удалось")
            raise RuntimeError("ShortMemory database is not available.")

    # Закрытие соединения с БД
    async def close(self):
        logger.debug("Закрытие соединения с БД")
        try:
            if self._db:                      # Если есть подключение
                await self._db.close()        # Закрываем его
                self._db = None               # Обнуляем
                logger.debug("БД успешно закрыта")
        except Exception as e:
            self._log_exception("close failed", e)  # Логируем ошибку

    # Добавление сообщения в историю диалога
    async def add_message(self, user_id: str, agent_id: str, message: str, role: str):
        logger.debug(f"Добавление сообщения: user_id={user_id}, agent_id={agent_id}, role={role}")
        try:
            await self._ensure_db()                           # Убедиться, что БД доступна
            timestamp = datetime.utcnow().isoformat()         # Получаем текущий UTC timestamp
            await self._db.execute(                           # Вставка новой записи
                "INSERT INTO memory (user_id, agent_id, message, role, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, agent_id, message, role, timestamp)
            )
            logger.debug("Сообщение вставлено")
            await self._db.commit()                           # Сохраняем изменения
            logger.debug("Коммит выполнен")
            await self._enforce_max_pairs(user_id, agent_id)  # Удаляем старые записи, если их слишком много
        except Exception as e:
            self._log_exception("add_message failed", e)      # Логируем ошибку

    # Удаление старых пар, если превышено max_pairs
    async def _enforce_max_pairs(self, user_id: str, agent_id: str):
        logger.debug(f"Проверка количества сообщений для user_id={user_id}, agent_id={agent_id}")
        try:
            await self._ensure_db()  # Проверка подключения к БД
            async with self._db.execute("""  # Получаем все id записей по user/agent в порядке убывания времени
                SELECT id FROM memory WHERE user_id = ? AND agent_id = ?
                ORDER BY timestamp DESC
            """, (user_id, agent_id)) as cursor:
                ids = [row[0] async for row in cursor]  # Извлекаем все id
            logger.debug(f"Получено {len(ids)} сообщений")
            if len(ids) > self.max_pairs * 2:  # Если количество записей превышает лимит пар
                to_delete = ids[self.max_pairs * 2:]  # Выбираем лишние записи
                await self._db.executemany("DELETE FROM memory WHERE id = ?", [(i,) for i in to_delete])  # Удаляем
                await self._db.commit()  # Сохраняем изменения
                logger.debug(f"Удалено {len(to_delete)} старых сообщений")
        except Exception as e:
            self._log_exception("_enforce_max_pairs failed", e)  # Логируем ошибку

    # Получение истории сообщений, сгруппированной по парам user/agent
    async def get_history(self, user_id: str, agent_id: str):
        logger.debug(f"Получение истории сообщений: user_id={user_id}, agent_id={agent_id}")
        try:
            await self._ensure_db()  # Проверяем доступность БД
            async with self._db.execute("""  # Получаем сообщения по user/agent в порядке возрастания времени
                SELECT message, role FROM memory
                WHERE user_id = ? AND agent_id = ?
                ORDER BY timestamp ASC
            """, (user_id, agent_id)) as cursor:
                messages = await cursor.fetchall()  # Получаем все строки
            logger.debug(f"Получено {len(messages)} записей")
            pairs = []         # Результирующий список пар сообщений
            pair = {}          # Временный словарь для текущей пары
            for msg, role in messages:  # Проходим по всем сообщениям
                pair[role] = msg        # Сохраняем сообщение по роли
                if "user" in pair and "agent" in pair:  # Если есть обе роли
                    pairs.append(pair)                  # Добавляем в список
                    pair = {}                           # Начинаем новую пару
            logger.debug(f"Возвращено {len(pairs)} пар сообщений")
            return pairs
        except Exception as e:
            self._log_exception("get_history failed", e)  # Логируем ошибку
            return []                                     # Возвращаем пустой список при ошибке

    # Очистка устаревших сообщений на основе TTL
    async def cleanup_expired_dialogs(self):
        logger.debug("Очистка устаревших сообщений")
        try:
            await self._ensure_db()  # Убеждаемся, что подключение к БД есть
            expiration_threshold = (datetime.utcnow() - timedelta(minutes=self.ttl_minutes)).isoformat()  # Считаем порог времени
            await self._db.execute("DELETE FROM memory WHERE timestamp < ?", (expiration_threshold,))  # Удаляем старые записи
            await self._db.commit()  # Подтверждаем изменения
            logger.debug("Очистка завершена успешно")
        except Exception as e:
            self._log_exception("cleanup_expired_dialogs failed", e)  # Логируем ошибку
