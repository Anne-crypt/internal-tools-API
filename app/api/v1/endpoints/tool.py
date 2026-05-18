from decimal import Decimal
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.tool import tool_controller
from app.database import get_db
from app.schemas.api.tool import ToolPaginatedResponse, ToolDetailOut, ToolCreateIn, ToolCreateOut

router = APIRouter()


@router.get("", response_model=ToolPaginatedResponse, summary="Filtrer et paginer les outils business")
async def get_tools(
    *,
    db: AsyncSession = Depends(get_db),
    department: str | None = Query(None, description="Filtrer par département (ex: Engineering)"),
    status: str | None = Query(None, description="Filtrer par statut (active, deprecated, trial)"),
    min_cost: Decimal | None = Query(None, description="Coût mensuel minimum"),
    max_cost: Decimal | None = Query(None, description="Coût mensuel maximum"),
    category: str | None = Query(None, alias="category", description="Nom de la catégorie (ex: Development)"),
    page: int = Query(1, ge=1, description="Numéro de la page"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    sort_by: str = Query("name", description="Champ de tri (name, cost, date)"),
    sort_order: str = Query("asc", description="Sens du tri (asc, desc)")
) -> Any:
    """
    Récupère la liste des outils avec un filtrage multicritère,
    une pagination et un système de tri dynamique.
    """
    # On passe par le Controller pour centraliser la logique métier.
    result = await tool_controller.get_filtered_tools_for_business(
        db,
        department=department,
        status=status,
        min_cost=min_cost,
        max_cost=max_cost,
        category=category,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return result

@router.get("/{tool_id}", response_model=ToolDetailOut, summary="Obtenir le détail financier complet d'un outil")
async def get_tool_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    tool_id: int = Path(..., ge=1, description="L'identifiant numérique de l'outil")
) -> Any:
    """Récupère toutes les informations d'un outil avec ses métriques et coûts totaux."""
    tool_detail = await tool_controller.get_tool_detail(db, tool_id=tool_id)

    if not tool_detail:
        raise HTTPException(status_code=404, detail="Outil SaaS introuvable")

    return tool_detail

@router.post(
    "",
    response_model=ToolCreateOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel outil business"
)
async def create_tool(
    *,
    db: AsyncSession = Depends(get_db),
    payload: ToolCreateIn
) -> Any:
    """Ajoute un nouvel outil dans le catalogue après validations strictes."""
    try:
        new_tool = await tool_controller.create_new_tool(db, tool_in=payload)

        # Formatage de la réponse pour mapper l'objet Category imbriqué vers le champ plat 'category'
        return {
            "id": new_tool.id,
            "name": new_tool.name,
            "description": new_tool.description,
            "vendor": new_tool.vendor,
            "website_url": new_tool.website_url,
            "category": new_tool.category.name, # Extraction du JOIN
            "monthly_cost": float(new_tool.monthly_cost),
            "owner_department": new_tool.owner_department,
            "status": new_tool.status,
            "active_users_count": new_tool.active_users_count,
            "created_at": new_tool.created_at,
            "updated_at": new_tool.updated_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))