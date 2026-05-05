from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlmodel import Session, select, SQLModel


# This represents our generic SQLModel type
ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """
    A generic repository providing standard CRUD operations.
    This is the Python equivalent of Spring Data's `JpaRepository` or `CrudRepository`.
    """
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Find by ID"""
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Find all with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, obj_in: ModelType) -> ModelType:
        """Save a new entity"""
        self.session.add(obj_in)
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in

    def update(self, db_obj: ModelType) -> ModelType:
        """Update an existing entity"""
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Delete an entity by ID"""
        obj = self.session.get(self.model, id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False