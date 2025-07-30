import chromadb  # Импорт основной библиотеки ChromaDB
from chromadb.api.models.Collection import Collection  # Импорт класса Collection для работы с коллекциями
from openai import OpenAI  # Импорт клиента OpenAI
from typing import List, Optional, Dict  # Импорт аннотаций типов
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # Импорт функции эмбеддинга от OpenAI
import uuid  # Импорт модуля для генерации уникальных идентификаторов
import time  # Импорт модуля времени
import os  # Импорт модуля для работы с переменными окружения
import asyncio  # Импорт модуля асинхронного программирования
import logging  # Импорт модуля логгирования
from collections import defaultdict  # Импорт defaultdict для создания словаря с значением по умолчанию
from chromadb.config import Settings  # Импорт конфигураций ChromaDB

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Фабрика клиентов ChromaDB — обеспечивает переиспользование одного клиента
class ChromaClientFactory:
    _client = None  # Статическая переменная для хранения клиента

    @classmethod
    def get_client(cls):
        # Возвращаем уже инициализированный клиент, если он есть
        if cls._client is not None:
            return cls._client
        # Определяем среду: ephemeral (в тестах) или persistent (по умолчанию)
        env = os.getenv("APP_ENV", "production").lower()
        if env == "test":
            cls._client = chromadb.EphemeralClient()  # Временный клиент для тестов
        else:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")  # Путь для сохранения данных
            cls._client = chromadb.PersistentClient(path=persist_dir)  # Постоянный клиент
        return cls._client  # Возвращаем клиента

# Класс долговременной памяти, основанный на ChromaDB
class LongMemory:
    def __init__(self, collection_name: str = "long_term_memory", openai_api_key: str = "...", ttl_seconds: Optional[int] = None, client=None):
        # Инициализация клиента OpenAI
        self.openai = OpenAI(api_key=openai_api_key)
        # Создание функции эмбеддинга от OpenAI
        self.embedding_fn = OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-small")
        # Получаем или создаем клиента Chroma
        self.client = client or ChromaClientFactory.get_client()
        # Получаем или создаем коллекцию
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "hnsw:M": 32, "hnsw:construction_ef": 128},
            embedding_function=self.embedding_fn
        )
        self.ttl_seconds = ttl_seconds  # Устанавливаем TTL для записей
        self._locks = defaultdict(asyncio.Lock)  # Создаем словарь блокировок для защиты от race conditions

    # Вспомогательный метод для логгирования исключений
    def _log_exception(self, message: str, exc: Exception):
        logger.exception(f"[LongMemory] {message}: {type(exc).__name__} - {exc}")

    # Вычисляем адаптивное значение top_k в зависимости от длины текста
    def _adaptive_top_k(self, text: str, max_k: int = 5) -> int:
        length = len(text)
        if length < 100:
            return 1
        elif length < 300:
            return 3
        return max_k

    # Возвращает текущую временную метку
    def _current_timestamp(self) -> float:
        return time.time()

    # Проверка, истек ли срок жизни записи
    def _is_expired(self, last_used: float, threshold: float) -> bool:
        return last_used < threshold

    # Поиск записей по тексту и фильтру (например, по user_id)
    async def query_by_metadata(self, filter: Dict, text: str, top_k: int = 3) -> List[dict]:
        logger.debug(f"[LongMemory][query_by_metadata] получил аргументы: filter={filter}, text={text}, top_k={top_k}")
        try:
            adaptive_k = self._adaptive_top_k(text, top_k)
            results = self.collection.query(query_texts=[text], n_results=adaptive_k, where=filter)
            for i in range(len(results["ids"][0])):
                await self._touch_record(results["ids"][0][i])
            output = [
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["documents"][0]))
                if not self._is_expired(results["metadatas"][0][i].get("_last_used", 0), self._current_timestamp() - (self.ttl_seconds or 0))
            ]
            logger.debug(f"[LongMemory][query_by_metadata] вернул результат: {output}")
            return output
        except Exception as e:
            self._log_exception("query_by_metadata failed", e)
            return []

    # Обновление поля _last_used записи по ее ID
    async def _touch_record(self, record_id: str):
        logger.debug(f"[LongMemory][_touch_record] обновление _last_used для записи: {record_id}")
        lock = self._locks[record_id]
        async with lock:
            try:
                record = self.collection.get(ids=[record_id])
                if record["metadatas"]:
                    metadata = record["metadatas"][0]
                    metadata["_last_used"] = self._current_timestamp()
                    text = record["documents"][0]
                    self.collection.update(ids=[record_id], documents=[text], metadatas=[metadata])
            except Exception as e:
                self._log_exception(f"_touch_record failed for {record_id}", e)

    # Добавление новой записи
    async def add_record(self, text: str, record_id: Optional[str] = None, metadata: Optional[dict] = None) -> Optional[str]:
        logger.debug(f"[LongMemory][add_record] получил аргументы: text={text}, record_id={record_id}, metadata={metadata}")
        try:
            record_id = record_id or str(uuid.uuid4())
            metadata = metadata or {}
            now = self._current_timestamp()
            metadata.update({"_created": now, "_last_used": now})
            self.collection.add(documents=[text], ids=[record_id], metadatas=[metadata])
            logger.debug(f"[LongMemory][add_record] вернул результат: {record_id}")
            return record_id
        except Exception as e:
            self._log_exception("add_record failed", e)
            return None

    # Удаление записи по идентификатору
    async def delete_record(self, record_id: str):
        logger.debug(f"[LongMemory][delete_record] получил аргумент: record_id={record_id}")
        try:
            self.collection.delete(ids=[record_id])
            logger.debug(f"[LongMemory][delete_record] успешно удалён: {record_id}")
        except Exception as e:
            self._log_exception(f"delete_record failed for {record_id}", e)

    # Обновление записи, если она существует, или добавление новой
    async def upsert_record(self, text: str, record_id: str, metadata: Optional[dict] = None):
        logger.debug(f"[LongMemory][upsert_record] получил аргументы: text={text}, record_id={record_id}, metadata={metadata}")
        try:
            now = self._current_timestamp()
            metadata = metadata or {}
            try:
                record = self.collection.get(ids=[record_id])
            except Exception:
                record = {"ids": []}
            if record["ids"]:
                old_meta = record["metadatas"][0] or {}
                old_meta.update(metadata)
                old_meta["_last_used"] = now
                self.collection.update(ids=[record_id], documents=[text], metadatas=[old_meta])
            else:
                metadata.update({"_created": now, "_last_used": now})
                self.collection.add(documents=[text], ids=[record_id], metadatas=[metadata])
            logger.debug(f"[LongMemory][upsert_record] завершено для record_id={record_id}")
            return record_id
        except Exception as e:
            self._log_exception("upsert_record failed", e)
            return None

    # Пакетное добавление записей
    async def batch_add(self, texts: List[str], ids: Optional[List[str]] = None, metadatas: Optional[List[dict]] = None):
        logger.debug(f"[LongMemory][batch_add] получил аргументы: texts={texts}, ids={ids}, metadatas={metadatas}")
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
            if metadatas is None:
                metadatas = [{} for _ in texts]
            now = self._current_timestamp()
            for meta in metadatas:
                meta.update({"_created": now, "_last_used": now})
            self.collection.add(documents=texts, ids=ids, metadatas=metadatas)
            logger.debug(f"[LongMemory][batch_add] добавлены записи: {ids}")
            return ids
        except Exception as e:
            self._log_exception("batch_add failed", e)
            return []

    # Получение всех записей, с учётом срока годности (TTL)
    async def get_all_records(self) -> List[dict]:
        logger.debug(f"[LongMemory][get_all_records] вызван")
        try:
            results = self.collection.get()
            for record_id in results["ids"]:
                await self._touch_record(record_id)
            output = [
                {
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                }
                for i in range(len(results["documents"]))
                if not self._is_expired(results["metadatas"][i].get("_last_used", 0), self._current_timestamp() - (self.ttl_seconds or 0))
            ]
            logger.debug(f"[LongMemory][get_all_records] вернул {len(output)} записей")
            return output
        except Exception as e:
            self._log_exception("get_all_records failed", e)
            return []

    # Получение записей, связанных с конкретным пользователем
    async def get_user_memory(self, user_id: str) -> List[dict]:
        logger.debug(f"[LongMemory][get_user_memory] получил аргумент: user_id={user_id}")
        try:
            results = self.collection.get(where={"user_id": user_id})
            for record_id in results["ids"]:
                await self._touch_record(record_id)
            output = [
                {
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                }
                for i in range(len(results["documents"]))
                if not self._is_expired(results["metadatas"][i].get("_last_used", 0), self._current_timestamp() - (self.ttl_seconds or 0))
            ]
            logger.debug(f"[LongMemory][get_user_memory] вернул {len(output)} записей")
            return output
        except Exception as e:
            self._log_exception(f"get_user_memory failed for {user_id}", e)
            return []

    # Очистка устаревших записей на основе TTL
    async def cleanup_expired(self, *, before: Optional[float] = None):
        logger.debug(f"[LongMemory][cleanup_expired] вызван с before={before}")
        if self.ttl_seconds is None:
            logger.debug(f"[LongMemory][cleanup_expired] завершён без удаления (TTL отключён)")
            return
        try:
            before = before or self._current_timestamp() - self.ttl_seconds
            expired = self.collection.get(where={"_last_used": {"$lt": before}})
            ids_to_delete = expired["ids"]
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.debug(f"[LongMemory][cleanup_expired] удалено {len(ids_to_delete)} записей")
        except Exception as e:
            self._log_exception("cleanup_expired failed", e)
