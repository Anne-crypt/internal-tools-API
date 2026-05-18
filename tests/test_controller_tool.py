import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import HttpUrl
from app.controllers.tool import tool_controller
from app.schemas.api.tool import ToolCreateIn, DepartmentType, ToolUpdateIn, ToolStatusType

# Tous les tests de ce fichier sont asynchrones
pytestmark = pytest.mark.asyncio

async def test_get_filtered_tools_no_filters(db_session: AsyncSession, seed_data):
    """Test sans aucun filtre via le Controller : doit tout renvoyer formaté."""
    result = await tool_controller.get_filtered_tools_for_business(db_session, page=1, limit=10)

    assert len(result["data"]) == 3
    assert result["total"] == 3
    assert "filters_applied" in result


async def test_get_filtered_tools_by_department_and_status(db_session: AsyncSession, seed_data):
    """Test du filtre combiné via le Controller."""
    result = await tool_controller.get_filtered_tools_for_business(
        db_session, department="Engineering", status="active"
    )

    assert len(result["data"]) == 2
    assert result["filters_applied"]["department"] == "Engineering"
    assert result["filters_applied"]["status"] == "active"

    names = [t["name"] for t in result["data"]]
    assert "Slack" in names
    assert "Jira" in names
    assert "Zoom" not in names


async def test_get_filtered_tools_by_cost_and_category(db_session: AsyncSession, seed_data):
    """Test du filtre coût et catégorie via le Controller."""
    result = await tool_controller.get_filtered_tools_for_business(
        db_session, min_cost=Decimal("10.00"), max_cost=Decimal("50.00"), category="Development"
    )

    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "Jira"


async def test_get_filtered_tools_validation_error(db_session: AsyncSession, seed_data):
    """Test de la logique métier : le coût min ne peut pas être supérieur au coût max."""
    with pytest.raises(ValueError) as exc_info:
        await tool_controller.get_filtered_tools_for_business(
            db_session, min_cost=Decimal("100.00"), max_cost=Decimal("50.00")
        )

    assert str(exc_info.value) == "Le coût minimum ne peut pas être supérieur au coût maximum"


async def test_get_tool_detail_success(db_session: AsyncSession, seed_data):
    """Test de récupération réussie avec calcul du coût total et métriques."""
    # Dans notre seed_data, Jira a l'ID 2 (généralement), monthly_cost = 45.00 et active_users = 10
    # Le coût total doit être de 450.0
    result = await tool_controller.get_tool_detail(db_session, tool_id=2)

    assert result is not None
    assert result["name"] == "Jira"
    assert result["total_monthly_cost"] == 450.0  # Validation du calcul financier
    assert result["usage_metrics"]["last_30_days"]["total_sessions"] == 127


async def test_get_tool_detail_not_found(db_session: AsyncSession, seed_data):
    """Test de la gestion du cas 404 (outil inexistant)."""
    result = await tool_controller.get_tool_detail(db_session, tool_id=999)
    assert result is None


async def test_create_tool_success(db_session: AsyncSession, seed_data):
    """Test de création réussie avec des données valides."""
    payload = ToolCreateIn(
        name="Linear",
        description="Issue tracking",
        vendor="Linear Inc",
        website_url=HttpUrl("https://linear.app"),
        category_id=1,  # "Development" ou "Communication" inséré par seed_data
        monthly_cost=Decimal("8.00"),
        owner_department=DepartmentType.ENGINEERING
    )

    new_tool = await tool_controller.create_new_tool(db_session, tool_in=payload)
    assert new_tool.id is not None
    assert new_tool.name == "Linear"
    assert new_tool.active_users_count == 0
    assert new_tool.status == "active"

async def test_create_tool_duplicate_name(db_session: AsyncSession, seed_data):
    """Test qu'on ne peut pas créer un outil avec un nom déjà existant (ex: Jira)."""
    payload = ToolCreateIn(
        name="Jira",  # Déjà présent dans seed_data
        vendor="Atlassian",
        website_url=HttpUrl("https://www.atlassian.com/software/jira"),
        category_id=1,
        monthly_cost=Decimal("45.00"),
        owner_department=DepartmentType.ENGINEERING
    )

    with pytest.raises(ValueError) as exc_info:
        await tool_controller.create_new_tool(db_session, tool_in=payload)
    assert "existe déjà" in str(exc_info.value)

async def test_create_tool_invalid_category(db_session: AsyncSession, seed_data):
    """Test qu'on refuse la création si la catégorie n'existe pas."""
    payload = ToolCreateIn(
        name="Figma",
        vendor="Figma",
        website_url=HttpUrl("https://www.figma.com"),
        category_id=999,  # Inexistant
        monthly_cost=Decimal("15.00"),
        owner_department=DepartmentType.DESIGN
    )

    with pytest.raises(ValueError) as exc_info:
        await tool_controller.create_new_tool(db_session, tool_in=payload)
    assert "n'existe pas" in str(exc_info.value)

async def test_update_tool_success(db_session: AsyncSession, seed_data):
    """Test d'une mise à jour partielle réussie (prix, statut, description)."""
    payload = ToolUpdateIn.model_validate({
        "monthly_cost": Decimal("7.00"),
        "status": ToolStatusType.DEPRECATED,
        "description": "Updated description after renewal",
    })

    # On modifie l'outil avec l'ID 1 (Slack par exemple)
    updated = await tool_controller.update_existing_tool(db_session, tool_id=1, tool_in=payload)

    assert updated is not None
    assert updated.monthly_cost == Decimal("7.00")
    assert updated.status == "deprecated"
    assert updated.description == "Updated description after renewal"
    assert updated.name == "Slack"  # Les champs non modifiés restent intacts

async def test_update_tool_not_found(db_session: AsyncSession, seed_data):
    """Test qu'un outil inexistant renvoie None (déclenchant un 404)."""
    payload = ToolUpdateIn.model_validate({"monthly_cost": Decimal("10.00")})
    result = await tool_controller.update_existing_tool(db_session, tool_id=999, tool_in=payload)
    assert result is None