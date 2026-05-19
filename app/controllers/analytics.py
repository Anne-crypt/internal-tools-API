from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from typing import Literal
from app.models.tool import Tool
from app.models.category import Category
from app.models.cost_tracking import CostTracking
from app.schemas.enums import DepartmentType

from app.schemas.api.analytics import (
    AnalyticsSavingsAnalysis,
    AnalyticsSummary,
    DepartmentCostResponse,
    DepartementCostItem,
    LowUsageToolDetail,
    LowUsageToolsResponse,
    ToolCostDetail,
    AnalyticsExpensiveToolsSummary,
    ExpensiveToolsResponse,
    ToolsByCategoryResponse,
    AnalyticsCategoryInsights,
    CategoryCostDetail,
)


class AnalyticsController:
    async def get_department_costs_summary(
        self, db: AsyncSession, sort_by: str = "total_cost", order: str = "desc"
    ) -> DepartmentCostResponse:
        """Récupère les coûts totaux par département et une synthèse globale."""

        @dataclass
        class DepartmentAnalyticsRow:
            department: DepartmentType
            total_cost: float
            total_count: int
            total_users: int
            average_cost_per_tool: float
            cost_percentage: float

        stmt_dept = (
            select(
                Tool.owner_department.label("department"),
                func.sum(CostTracking.total_monthly_cost).label("total_cost"),
                func.count(Tool.id.distinct()).label("tools_count"),
                func.sum(CostTracking.active_users_count).label("total_users"),
                (
                    func.sum(CostTracking.total_monthly_cost)
                    / func.count(Tool.id.distinct())
                ).label("average_cost_per_tool"),
            )
            .join(CostTracking, Tool.id == CostTracking.tool_id)
            .group_by(Tool.owner_department)
        )

        stmt_total = select(func.sum(CostTracking.total_monthly_cost))
        total_company_cost = float((await db.execute(stmt_total)).scalar() or 0.0)

        result_dept = await db.execute(stmt_dept)

        departments_data: list[DepartmentAnalyticsRow] = []
        for row in result_dept.all():
            dept_cost = float(row.total_cost or 0.0)
            cost_percentage = 0.0
            if total_company_cost > 0:
                cost_percentage = round((dept_cost / total_company_cost) * 100, 1)

            departments_data.append(
                DepartmentAnalyticsRow(
                    department=row.department,
                    total_cost=round(dept_cost, 2),
                    total_count=int(row.tools_count),
                    total_users=int(row.total_users or 0),
                    average_cost_per_tool=round(
                        float(row.average_cost_per_tool or 0.0), 2
                    ),
                    cost_percentage=cost_percentage,
                )
            )

        most_expensive_department: DepartmentType | None = None
        if departments_data:
            most_expensive_department = max(
                sorted(departments_data, key=lambda item: item.department),
                key=lambda item: item.total_cost,
            ).department

        reverse_order = order == "desc"
        if sort_by == "department":
            final_sorted_data = sorted(
                departments_data,
                key=lambda item: item.department,
                reverse=reverse_order,
            )
        elif sort_by == "total_count":
            final_sorted_data = sorted(
                departments_data,
                key=lambda item: item.total_count,
                reverse=reverse_order,
            )
        elif sort_by == "total_users":
            final_sorted_data = sorted(
                departments_data,
                key=lambda item: item.total_users,
                reverse=reverse_order,
            )
        else:
            final_sorted_data = sorted(
                departments_data,
                key=lambda item: item.total_cost,
                reverse=reverse_order,
            )

        summary_department: DepartmentType = (
            most_expensive_department
            if most_expensive_department is not None
            else DepartmentType.ENGINEERING
        )

        return DepartmentCostResponse(
            department_costs=[
                DepartementCostItem(
                    department=item.department,
                    total_cost=item.total_cost,
                    total_count=item.total_count,
                    total_users=item.total_users,
                    average_cost_per_tool=item.average_cost_per_tool,
                    cost_percentage=item.cost_percentage,
                )
                for item in final_sorted_data
            ],
            summary=AnalyticsSummary(
                total_company_cost=round(total_company_cost, 2),
                departments_count=len(departments_data),
                most_expensive_department=summary_department,
            ),
        )

    async def get_expensive_tools(
        self, db: AsyncSession, min_cost: float = 0.0, limit: int = 10
    ) -> ExpensiveToolsResponse:
        # 1. Calcul de la moyenne pondérée globale de l'entreprise (avg_cost_per_user_company)
        # On exclut les outils qui ont 0 utilisateur actif pour éviter de fausser la moyenne ou d'avoir une division par zéro SQL
        avg_stmt = select(
            func.sum(Tool.monthly_cost).label("total_cost"),
            func.sum(Tool.active_users_count).label("total_users"),
        ).where(Tool.active_users_count > 0)

        avg_result = await db.execute(avg_stmt)
        avg_row = avg_result.first()

        # Gestion de la moyenne pondérée globale
        total_company_cost = (
            float(avg_row.total_cost) if avg_row and avg_row.total_cost else 0.0
        )
        total_company_users = (
            avg_row.total_users if avg_row and avg_row.total_users else 0
        )

        if total_company_users > 0:
            avg_cost_per_user_company = round(
                total_company_cost / total_company_users, 2
            )
        else:
            avg_cost_per_user_company = 0.0

        # 2. Récupération des outils avec filtres, tri et limite
        tools_stmt = (
            select(Tool)
            .where(Tool.monthly_cost >= min_cost)
            .order_by(Tool.monthly_cost.desc())
            .limit(limit)
        )

        tools_result = await db.execute(tools_stmt)
        tools = tools_result.scalars().all()

        # 3. Traitement des outils et calcul des métriques individuelles
        tool_details = []
        potential_savings_identified = 0.0

        for tool in tools:
            tool_monthly_cost = float(tool.monthly_cost) if tool.monthly_cost else 0.0
            efficiency_rating: Literal["excellent", "good", "average", "low"]

            # Calcul du cost_per_user précis avec gestion de la division par zéro
            if tool.active_users_count > 0:
                cost_per_user = round(
                    float(tool.monthly_cost / tool.active_users_count), 2
                )
            else:
                cost_per_user = 0.0  # Choix sécurisé si pas d'utilisateur actif

            # Attribution du rating d'efficacité basé sur la logique métier de Jennifer
            # (Comparaison de cost_per_user vs avg_cost_per_user_company)
            if avg_cost_per_user_company == 0:
                efficiency_rating = "average"  # Valeur par défaut si aucune moyenne entreprise n'est calculable
            else:
                ratio = cost_per_user / avg_cost_per_user_company
                if ratio < 0.5:
                    efficiency_rating = "excellent"
                elif ratio <= 0.8:
                    efficiency_rating = "good"
                elif ratio <= 1.2:
                    efficiency_rating = "average"
                else:
                    efficiency_rating = "low"

            # Calcul des économies potentielles (Somme des coûts des outils "low")
            if efficiency_rating == "low":
                potential_savings_identified += tool_monthly_cost

            # On build l'objet Pydantic pour cet outil
            tool_details.append(
                ToolCostDetail(
                    id=tool.id,
                    name=tool.name,
                    monthly_cost=tool_monthly_cost,
                    active_users_count=tool.active_users_count,
                    cost_per_user=cost_per_user,
                    department=tool.owner_department,
                    vendor=tool.vendor or "Unknown",
                    efficiency_rating=efficiency_rating,
                )
            )

        # 4. Construction de la réponse globale finale
        return ExpensiveToolsResponse(
            data=tool_details,
            analysis=AnalyticsExpensiveToolsSummary(
                total_tools_analyzed=len(tool_details),
                avg_cost_per_user_company=avg_cost_per_user_company,
                potential_savings_identified=round(potential_savings_identified, 2),
            ),
        )

    async def get_tools_by_category(self, db: AsyncSession) -> ToolsByCategoryResponse:
        # 1. Étape 1 : Calculer le budget total global de l'entreprise
        total_budget_stmt = select(func.sum(Tool.monthly_cost))
        total_budget_result = await db.execute(total_budget_stmt)
        total_budget_raw = total_budget_result.scalar()
        company_total_cost = float(total_budget_raw) if total_budget_raw else 0.0

        # 2. Étape 2 : Requête groupée avec JOIN entre Tool et Category
        category_stmt = (
            select(
                Category.name.label("category_name"),
                func.count(Tool.id).label("tools_count"),
                func.sum(Tool.monthly_cost).label("total_cost"),
                func.sum(Tool.active_users_count).label("total_users"),
            )
            .join(Tool, Tool.category_id == Category.id)
            .group_by(Category.id, Category.name)
        )

        category_result = await db.execute(category_stmt)
        rows = category_result.all()

        # 3. Étape 3 : Traitement des données par catégorie
        categories_details = []

        # Variables pour calculer les insights métier
        max_cost = -1.0
        most_expensive_category = "None"

        min_cost_per_user = float("inf")
        most_efficient_category = "None"

        for row in rows:
            # Sécurisation des types pour Mypy
            cat_name = str(row.category_name)
            tools_count = int(row.tools_count) if row.tools_count else 0
            total_cost = float(row.total_cost) if row.total_cost else 0.0
            total_users = int(row.total_users) if row.total_users else 0

            # Pourcentage du budget (évite la division par zéro si budget global nul)
            if company_total_cost > 0:
                percentage_of_budget = round((total_cost / company_total_cost) * 100, 1)
            else:
                percentage_of_budget = 0.0

            # Coût moyen par utilisateur (sécurité division par zéro)
            if total_users > 0:
                average_cost_per_user = round(total_cost / total_users, 2)
            else:
                average_cost_per_user = 0.0

            # --- Calcul des Insights ---
            # Insight 1 : La plus chère
            if total_cost > max_cost:
                max_cost = total_cost
                most_expensive_category = cat_name
            elif total_cost == max_cost:
                # Règle de départage optionnelle : ordre alphabétique en cas d'égalité stricte de coût
                most_expensive_category = min(most_expensive_category, cat_name)

            # Insight 2 : La plus efficace (coût par utilisateur le plus bas)
            # Clarification : On exclut complètement les catégories sans utilisateurs (> 0)
            if total_users > 0:
                if average_cost_per_user < min_cost_per_user:
                    min_cost_per_user = average_cost_per_user
                    most_efficient_category = cat_name
                elif average_cost_per_user == min_cost_per_user:
                    # Clarification : En cas d'égalité, ordre alphabétique du category_name
                    most_efficient_category = min(most_efficient_category, cat_name)

            # Construction de l'objet de détail pour la liste principale
            categories_details.append(
                CategoryCostDetail(
                    category_name=cat_name,
                    tools_count=tools_count,
                    total_cost=total_cost,
                    total_users=total_users,
                    percentage_of_budget=percentage_of_budget,
                    average_cost_per_user=average_cost_per_user,
                )
            )

        # 4. Étape 4 : Retourner la réponse complète
        return ToolsByCategoryResponse(
            data=categories_details,
            insights=AnalyticsCategoryInsights(
                most_expensive_category=most_expensive_category,
                most_efficient_category=most_efficient_category,
            ),
        )

    async def get_low_usage_tools(
        self, db: AsyncSession, max_users: int = 5
    ) -> LowUsageToolsResponse:
        # 1. Requête SQL pour filtrer les outils sous-utilisés
        # On inclut automatiquement les outils à 0 utilisateur (0 <= max_users est toujours vrai pour max_users >= 0)
        stmt = (
            select(Tool)
            .where(Tool.active_users_count <= max_users)
            .order_by(Tool.active_users_count.asc(), Tool.monthly_cost.desc())
        )

        result = await db.execute(stmt)
        tools = result.scalars().all()

        # 2. Initialisation des compteurs et variables
        tool_details = []
        potential_monthly_savings = 0.0

        for tool in tools:
            # Sécurisation des types pour Mypy
            tool_monthly_cost = float(tool.monthly_cost) if tool.monthly_cost else 0.0
            users_count = int(tool.active_users_count) if tool.active_users_count else 0
            warning_level: Literal["high", "medium", "low"]

            # Calcul du cost_per_user (gestion division par zéro)
            if users_count > 0:
                cost_per_user = round(tool_monthly_cost / users_count, 2)
            else:
                cost_per_user = 0.0

            # 3. Logique warning_level et potential_action
            # Règle : Les outils à 0 utilisateur passent automatiquement en "high"
            if users_count == 0 or cost_per_user > 50.0:
                warning_level = "high"
                potential_action = "Consider canceling or downgrading"
            elif 20.0 <= cost_per_user <= 50.0:
                warning_level = "medium"
                potential_action = "Review usage and consider optimization"
            else:
                warning_level = "low"
                potential_action = "Monitor usage trends"

            # 4. Calcul des économies (Somme des coûts des outils "high" et "medium")
            if warning_level in ["high", "medium"]:
                potential_monthly_savings += tool_monthly_cost

            # Construction de l'objet de détail
            tool_details.append(
                LowUsageToolDetail(
                    id=tool.id,
                    name=tool.name,
                    monthly_cost=tool_monthly_cost,
                    active_users_count=users_count,
                    cost_per_user=cost_per_user,
                    department=tool.owner_department,
                    vendor=tool.vendor or "Unknown",
                    warning_level=warning_level,
                    potential_action=potential_action,
                )
            )

        # 5. Calcul des économies annuelles
        potential_annual_savings = potential_monthly_savings * 12

        return LowUsageToolsResponse(
            data=tool_details,
            savings_analysis=AnalyticsSavingsAnalysis(
                total_underutilized_tools=len(tool_details),
                potential_monthly_savings=round(potential_monthly_savings, 2),
                potential_annual_savings=round(potential_annual_savings, 2),
            ),
        )


analytics_controller = AnalyticsController()
