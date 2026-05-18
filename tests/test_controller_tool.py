import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.controllers.tool import tool_controller

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
        db_session, min_cost=10.00, max_cost=50.00, category="Development"
    )

    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "Jira"


async def test_get_filtered_tools_validation_error(db_session: AsyncSession, seed_data):
    """Test de la logique métier : le coût min ne peut pas être supérieur au coût max."""
    with pytest.raises(ValueError) as exc_info:
        await tool_controller.get_filtered_tools_for_business(
            db_session, min_cost=100.00, max_cost=50.00
        )

    assert str(exc_info.value) == "Le coût minimum ne peut pas être supérieur au coût maximum"