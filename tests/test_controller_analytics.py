import pytest
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from app.controllers.analytics import analytics_controller
from app.schemas.api.analytics import DepartmentCostResponse, ExpensiveToolsResponse
from app.schemas.enums import DepartmentType

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

@pytest.mark.asyncio
async def test_get_expensive_tools_success():
    # 1. Session de base de données simulée
    mock_db = AsyncMock()

    # 2. Simulation du 1er execute() : Moyenne globale de l'entreprise
    # Total coûts = 3000€, Total users actifs = 100 -> Moyenne = 30€/user
    mock_avg_result = MagicMock()
    mock_avg_row = MagicMock()
    mock_avg_row.total_cost = 3000.0
    mock_avg_row.total_users = 100
    mock_avg_result.first.return_value = mock_avg_row

    # 3. Simulation du 2ème execute() : La liste des outils (triée par coût desc)
    mock_tools_result = MagicMock()

    # Outil 1 : CRM Enterprise (Coût: 1000, Users: 10 -> Cost/User: 100€)
    # Ratio = 100 / 30 = 3.33 (> 1.2) -> Rating: "low"
    tool_1 = SimpleNamespace(
        id=1,
        name="CRM Enterprise",
        monthly_cost=1000.0,
        active_users_count=10,
        vendor="BigCorp",
        owner_department=DepartmentType.SALES,
    )

    # Outil 2 : Slack Pro (Coût: 500, Users: 25 -> Cost/User: 20€)
    # Ratio = 20 / 30 = 0.66 (entre 0.5 et 0.8) -> Rating: "good"
    tool_2 = SimpleNamespace(
        id=2,
        name="Slack Pro",
        monthly_cost=500.0,
        active_users_count=25,
        vendor="Slack Inc",
        owner_department=DepartmentType.ENGINEERING,
    )

    tools_list = [tool_1, tool_2]
    mock_tools_result.scalars.return_value.all.return_value = tools_list

    # Configuration des retours successifs du db.execute
    mock_db.execute.side_effect = [mock_avg_result, mock_tools_result]

    # 4. Appel du contrôleur
    response = await analytics_controller.get_expensive_tools(db=mock_db, min_cost=100.0, limit=2)

    # 5. Assertions (Vérifications)
    assert isinstance(response, ExpensiveToolsResponse)

    # Vérification de l'analyse globale
    assert response.analysis.total_tools_analyzed == 2
    assert response.analysis.avg_cost_per_user_company == 30.0
    assert response.analysis.potential_savings_identified == 1000.0  # Seul le CRM est "low" (1000€)

    # Vérification des détails des outils
    assert response.data[0].name == "CRM Enterprise"
    assert response.data[0].cost_per_user == 100.0
    assert response.data[0].efficiency_rating == "low"
    assert response.data[0].department == "Sales"

    assert response.data[1].name == "Slack Pro"
    assert response.data[1].cost_per_user == 20.0
    assert response.data[1].efficiency_rating == "good"

@pytest.mark.asyncio
async def test_get_expensive_tools_zero_users_and_no_savings():
    # 1. Session DB simulée
    mock_db = AsyncMock()

    # 2. Moyenne globale de l'entreprise (100€ total / 10 users = 10€/user moyenne)
    mock_avg_result = MagicMock()
    mock_avg_row = MagicMock()
    mock_avg_row.total_cost = 100.0
    mock_avg_row.total_users = 10
    mock_avg_result.first.return_value = mock_avg_row

    # 3. Liste des outils avec un outil à 0 utilisateur (Division par zéro potentielle)
    mock_tools_result = MagicMock()

    # Outil avec 0 utilisateur actif -> Doit donner un cost_per_user de 0.0 et éviter le crash
    tool_unused = SimpleNamespace(
        id=3,
        name="Unused Tool",
        monthly_cost=50.0,
        active_users_count=0,
        vendor="Ghost Vendor",
        owner_department=DepartmentType.HR,
    )  # Ratio = 0 / 10 = 0 (< 0.5) -> Rating: "excellent"

    tools_list = [tool_unused]
    mock_tools_result.scalars.return_value.all.return_value = tools_list

    mock_db.execute.side_effect = [mock_avg_result, mock_tools_result]

    # 4. Appel du contrôleur
    response = await analytics_controller.get_expensive_tools(db=mock_db)

    # 5. Assertions
    assert response.analysis.total_tools_analyzed == 1
    assert response.data[0].cost_per_user == 0.0  # Sécurité division par zéro activée !
    assert response.data[0].efficiency_rating == "excellent"
    assert response.analysis.potential_savings_identified == 0.0  # Aucun outil "low", donc 0 économie