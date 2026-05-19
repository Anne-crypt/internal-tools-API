from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from app.models.tool import Tool
from app.models.cost_tracking import CostTracking
from app.schemas.enums import DepartmentType

from app.schemas.api.analytics import AnalyticsSummary, DepartmentCostResponse, DepartementCostItem



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
            )
        )


analytics_controller = AnalyticsController()


