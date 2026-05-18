from decimal import Decimal
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.tool import tool_crud


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

tool_controller = ToolController()