from decimal import Decimal
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.tool import tool_crud
from app.models.category import Category
from app.models.tool import Tool

from app.schemas.api.tool import ToolCreateIn

class ToolController:
    async def get_filtered_tools_for_business(
        self,
        db: AsyncSession,
        *,
        department: str | None = None,
        status: str | None = None,
        min_cost: Decimal | None = None,
        max_cost: Decimal | None = None,
        category: str | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> dict[str, Any]:
        """
        Controller gérant la logique métier pour le filtrage des outils.
        C'est ici qu'on ajoutera les validations métiers plus tard.
        """
        # Exemple de validation métier
        if min_cost is not None and max_cost is not None and min_cost > max_cost:
            # Ici on lèvera une exception personnalisée (on verra la gestion d'erreurs centrale après)
            raise ValueError("Le coût minimum ne peut pas être supérieur au coût maximum")

        # Appel de la couche ORM / CRUD
        return await tool_crud.get_filtered_tools(
            db,
            department=department,
            status=status,
            min_cost=min_cost,
            max_cost=max_cost,
            category_name=category,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )


    async def get_tool_detail(self, db: AsyncSession, tool_id: int) -> dict[str, Any] | None:
        """Gère la logique métier et les calculs financiers pour le détail d'un outil."""
        tool = await tool_crud.get_by_id_with_category(db, tool_id=tool_id)
        if not tool:
            return None

        # Logique métier : Calcul financier complet
        total_monthly_cost = float(tool.monthly_cost) * tool.active_users_count

        # Formatage de la réponse selon le contrat de Marcus
        return {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "vendor": tool.vendor,
            "website_url": tool.website_url,
            "category": tool.category.name,
            "monthly_cost": float(tool.monthly_cost),
            "owner_department": tool.owner_department,
            "status": tool.status,
            "active_users_count": tool.active_users_count,
            "total_monthly_cost": total_monthly_cost,
            "created_at": tool.created_at,
            "updated_at": tool.updated_at,
            # Mock des métriques en attendant une table dédiée
            "usage_metrics": {
                "last_30_days": {
                    "total_sessions": 127,  # Logique fictive demandée
                    "avg_session_minutes": 45
                }
            }
        }


    async def create_new_tool(self, db: AsyncSession, *, tool_in: ToolCreateIn) -> Tool:
        """Gère la logique métier et les validations d'existence avant création."""

        # 1. Validation : Est-ce que la catégorie existe en DB ?
        category_check = await db.execute(select(Category).where(Category.id == tool_in.category_id))
        if not category_check.scalar_one_or_none():
            raise ValueError(f"La catégorie avec l'ID {tool_in.category_id} n'existe pas")

        # 2. Validation : Unicité du nom de l'outil
        name_check = await db.execute(select(Tool).where(func.lower(Tool.name) == func.lower(tool_in.name)))
        if name_check.scalar_one_or_none():
            raise ValueError(f"Un outil avec le nom '{tool_in.name}' existe déjà")

        # 3. Appel du CRUD pour l'insertion
        return await tool_crud.create_tool(db, obj_in=tool_in)

tool_controller = ToolController()