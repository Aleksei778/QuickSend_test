from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.query(self.model_class).filter_by(id=id).first()

    def get_all(self) -> List[T]:
        return self.db.query(self.model_class).all()

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def update(self, obj: T) -> T:
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)

        if obj:
            self.db.delete(obj)
            self.db.commit()

            return True

        return False