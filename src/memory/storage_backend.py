from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class StorageBackend(ABC):
    """
    Abstract base class for pluggable memory storage backends.
    Implementations must provide async CRUD operations.
    """
    @abstractmethod
    async def store(self, entity: Any) -> str:
        pass

    @abstractmethod
    async def retrieve(self, entity_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        pass

    @abstractmethod
    async def search(self, query: Dict[str, Any], limit: int = 10) -> List[Any]:
        pass

class SQLiteStorageBackend(StorageBackend):
    """
    SQLite-based backend for persistent storage.
    This is a minimal scaffold for demonstration and extension.
    """
    def __init__(self, db_path: str):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            data TEXT
        )''')

    async def store(self, entity: Any) -> str:
        import json
        self.conn.execute(
            'REPLACE INTO entities (id, data) VALUES (?, ?)',
            (entity.id, json.dumps(entity.to_dict()))
        )
        self.conn.commit()
        return entity.id

    async def retrieve(self, entity_id: str) -> Optional[Any]:
        cursor = self.conn.execute('SELECT data FROM entities WHERE id=?', (entity_id,))
        row = cursor.fetchone()
        if row:
            import json
            return json.loads(row[0])
        return None

    async def delete(self, entity_id: str) -> bool:
        cur = self.conn.execute('DELETE FROM entities WHERE id=?', (entity_id,))
        self.conn.commit()
        return cur.rowcount > 0

    async def search(self, query: Dict[str, Any], limit: int = 10) -> List[Any]:
        # This is a stub: for demo, return all entities (real impl should filter by query)
        cursor = self.conn.execute('SELECT data FROM entities LIMIT ?', (limit,))
        import json
        return [json.loads(row[0]) for row in cursor.fetchall()]
