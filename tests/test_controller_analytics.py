import pytest
from unittest.mock import AsyncMock, MagicMock
from app.controllers.analytics import analytics_controller
from app.schemas.api.analytics import DepartmentCostResponse

@pytest.mark.asyncio
async def test_get_department_costs_summary_success():
    # 1. Préparation d'une session de base de données simulée
    mock_db = AsyncMock()

    # 2. Simulation de la réponse pour le coût total global (stmt_total)
    mock_total_result = MagicMock()
    mock_total_result.scalar.return_value = 1000.0

    # 3. Simulation de la réponse pour les départements (stmt_dept)
    mock_dept_result = MagicMock()

    # Création de fausses lignes (rows) comme celles retournées par SQLAlchemy
    row_eng = MagicMock(
        department="Engineering",
        total_cost=600.0,
        tools_count=3,
        total_users=50,
        average_cost_per_tool=200.0
    )
    row_eng.__getitem__.side_effect = lambda key: {"department": "Engineering", "total_cost": 600.0, "tools_count": 3, "total_users": 50, "average_cost_per_tool": 200.0}[key]
    row_hr = MagicMock(
        department="HR",
        total_cost=400.0,
        tools_count=2,
        total_users=10,
        average_cost_per_tool=200.0
    )

    row_hr.__getitem__.side_effect = lambda key: {"department": "HR", "total_cost": 400.0, "tools_count": 2, "total_users": 10, "average_cost_per_tool": 200.0}[key]

    rows_list = [row_eng, row_hr]
    mock_dept_result.all.return_value = rows_list
    mock_dept_result.__iter__.return_value = iter(rows_list)
    mock_dept_result.scalars.return_value.all.return_value = rows_list
    mock_dept_result.mappings.return_value.all.return_value = rows_list

    # On configure notre mock_db pour renvoyer d'abord le total, puis les départements
    mock_third_result = MagicMock()  # Un troisième résultat pour éviter les erreurs de "side_effect" si le code fait plus de 2 appels à execute()
    mock_db.execute.side_effect = [mock_total_result, mock_dept_result, mock_third_result]

    # 4. Appel de la fonction du contrôleur
    response = await analytics_controller.get_department_costs_summary(
        db=mock_db, sort_by="total_cost", order="desc"
    )

    # 5. Les vérifications (assertions)
    assert isinstance(response, DepartmentCostResponse)
    assert response.summary.total_company_cost == 1000.0
    assert response.summary.departments_count == 2

    departments = response.department_costs

    # Comme nous avons demandé un tri descendant par "total_cost",
    # Engineering (600€) doit être le premier élément [0]
    assert departments[0].department == "Engineering"
    assert departments[0].total_cost == 600.0
    assert departments[0].cost_percentage == 60.0  # 💡 Notre calcul à 60%
    assert departments[0].average_cost_per_tool == 200.0

    # HR (400€) doit être le second élément [1]
    assert departments[1].department == "HR"
    assert departments[1].total_cost == 400.0
    assert departments[1].cost_percentage == 40.0


@pytest.mark.asyncio
async def test_get_department_costs_summary_equality_rule():
    # 1. Session simulée
    mock_db = AsyncMock()

    # 2. Coût global (500 + 500 = 1000)
    mock_total_result = MagicMock()
    mock_total_result.scalar.return_value = 1000.0

    # 3. Deux départements avec le même coût maximal
    mock_dept_result = MagicMock()
    row_sales = MagicMock(
        department="Sales",
        total_cost=500.0,
        tools_count=2,
        total_users=15,
        average_cost_per_tool=250.0
    )
    row_sales.__getitem__.side_effect = lambda key: {"department": "Sales", "total_cost": 500.0, "tools_count": 2, "total_users": 15, "average_cost_per_tool": 250.0}[key]

    row_marketing = MagicMock(
        department="Marketing",
        total_cost=500.0,
        tools_count=2,
        total_users=20,
        average_cost_per_tool=250.0
    )
    row_marketing.__getitem__.side_effect = lambda key: {"department": "Marketing", "total_cost": 500.0, "tools_count": 2, "total_users": 20, "average_cost_per_tool": 250.0}[key]
    # On les insère exprès dans un ordre non alphabétique
    rows_equality_list = [row_sales, row_marketing]
    mock_dept_result.all.return_value = rows_equality_list
    mock_dept_result.__iter__.return_value = iter(rows_equality_list)
    mock_dept_result.scalars.return_value.all.return_value = rows_equality_list
    mock_dept_result.mappings.return_value.all.return_value = rows_equality_list
    mock_third_result = MagicMock()
    mock_db.execute.side_effect = [mock_total_result, mock_dept_result, mock_third_result]

    # 4. Appel du contrôleur
    response = await analytics_controller.get_department_costs_summary(db=mock_db)

    # 5. Validation de la règle d'égalité alphabétique
    assert response.summary.most_expensive_department == "Marketing"