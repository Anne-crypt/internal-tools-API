from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import User
from app.schemas.api.user import UserCreate  # Ton schéma d'API

class CRUDUser(CRUDBase[User, UserCreate, Any]):
    # On ajoute une méthode spécifique à User
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        return db.query(self.model).filter(self.model.email == email).first()

# On l'instantie pour l'importer directement ailleurs
user_crud = CRUDUser(User)