from typing import Any


class DocumentsCollection:
    def __init__(self) -> None:
        self.storage: dict[str, Any] = {}

    def store(self, id: str, obj: Any) -> None:
        self.storage[id] = obj

    def get(self, id: str) -> Any:
        return self.storage[id]

    def delete(self, id: str) -> None:
        del self.storage[id]


class Database:
    def __init__(self) -> None:
        self.collections: dict[str, DocumentsCollection] = {}

    def collection(self, name: str) -> DocumentsCollection:
        if name not in self.collections:
            self.collections[name] = DocumentsCollection()
        return self.collections[name]
