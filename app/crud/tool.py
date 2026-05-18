from decimal import Decimal
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.crud.base import CRUDBase
from app.models.tool import Tool
from app.models.category import Category
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.schemas.api.tool import ToolCreateIn


class CRUDTool(CRUDBase[Tool]):
    async def get_filtered_tools(
        self,
        db: AsyncSession,
        *,
        department: str | None = None,
        status: str | None = None,
        min_cost: Decimal | None = None,
        max_cost: Decimal | None = None,
        category_name: str | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "name",  # cost, name, date
        sort_order: str = "asc"  # asc, desc
    ) -> dict[str, Any]:

        # 1. Requête pour le TOTAL absolu d'outils en BDD (sans filtres)
        total_query = select(func.count()).select_from(Tool)
        total_result = await db.execute(total_query)
        total_count = total_result.scalar_one() or 0

        # 2. Construction de la requête principale avec jointure sur Category
        stmt = select(Tool).join(Tool.category)

        # 3. Application des filtres multiples combinables
        if department:
            stmt = stmt.where(Tool.owner_department == department)
        if status:
            stmt = stmt.where(Tool.status == status)
        if min_cost is not None:
            stmt = stmt.where(Tool.monthly_cost >= min_cost)
        if max_cost is not None:
            stmt = stmt.where(Tool.monthly_cost <= max_cost)
        if category_name:
            stmt = stmt.where(Category.name == category_name)

        # 4. Requête pour le compte FILTERED (après filtres, avant pagination)
        filtered_count_query = select(func.count()).select_from(stmt.subquery())
        filtered_result = await db.execute(filtered_count_query)
        filtered_count = filtered_result.scalar_one() or 0

        # 5. Gestion du Tri (Sorting)
        sort_attr: InstrumentedAttribute = Tool.name
        if sort_by == "cost":
            sort_attr = Tool.monthly_cost
        elif sort_by == "date":
            sort_attr = Tool.created_at

        if sort_order == "desc":
            stmt = stmt.order_by(sort_attr.desc())
        else:
            stmt = stmt.order_by(sort_attr.asc())

        # 6. Pagination (page/limit)
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        # On s'assure de charger la catégorie liée pour éviter le problème de N+1 requêtes
        stmt = stmt.options(joinedload(Tool.category))

        # Exécution
        result = await db.execute(stmt)
        tools = result.scalars().all()

        # 7. Formatage des données pour correspondre exactement au format attendu
        data_formatted = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "vendor": t.vendor,
                "category": t.category.name,  # Récupéré grâce au JOIN
                "monthly_cost": float(t.monthly_cost),
                "owner_department": t.owner_department,
                "status": t.status,
                "website_url": t.website_url,
                "active_users_count": t.active_users_count,
                "created_at": t.created_at.isoformat() + "Z" if t.created_at else None
            }
            for t in tools
        ]

        # Dictionnaire des filtres effectivement appliqués
        filters_applied: dict[str, Any] = {}
        if department:
            filters_applied["department"] = department
        if status:
            filters_applied["status"] = status
        if min_cost is not None:
            filters_applied["min_cost"] = float(min_cost)
        if max_cost is not None:
            filters_applied["max_cost"] = float(max_cost)
        if category_name:
            filters_applied["category"] = category_name

        return {
            "data": data_formatted,
            "total": total_count,
            "filtered": filtered_count,
            "filters_applied": filters_applied
        }

    async def get_by_id_with_category(self, db: AsyncSession, tool_id: int) -> Tool | None:
        """Récupère un outil par son ID avec sa catégorie préchargée."""
        stmt = (
            select(Tool)
            .where(Tool.id == tool_id)
            .options(joinedload(Tool.category))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tool(self, db: AsyncSession, *, obj_in: ToolCreateIn) -> Tool:
        """Insère un nouvel outil et recharge ses relations."""
        db_obj = Tool(
            name=obj_in.name,
            description=obj_in.description,
            vendor=obj_in.vendor,
            website_url=str(obj_in.website_url) if obj_in.website_url else None,
            category_id=obj_in.category_id,
            monthly_cost=obj_in.monthly_cost,
            owner_department=obj_in.owner_department.value if hasattr(obj_in.owner_department, 'value') else obj_in.owner_department,
            status="active",  # Valeur par défaut demandée
            active_users_count=0  # Initialisé à 0
        )
        db.add(db_obj)
        await db.commit()

        # On recharge l'objet avec sa catégorie pour le contrôleur
        stmt = select(Tool).where(Tool.id == db_obj.id).options(joinedload(Tool.category))
        result = await db.execute(stmt)
        return result.scalar_one()

tool_crud = CRUDTool(Tool)