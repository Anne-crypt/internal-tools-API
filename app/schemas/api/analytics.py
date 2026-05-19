
from pydantic import BaseModel

from app.schemas.enums import DepartmentType


class DepartementCostItem(BaseModel):
    department: DepartmentType
    total_cost: float
    total_count: int
    total_users: int
    average_cost_per_tool: float
    cost_percentage: float


class AnalyticsSummary(BaseModel):
    total_company_cost: float
    departments_count: int
    most_expensive_department: DepartmentType


class DepartmentCostResponse(BaseModel):
    department_costs: list[DepartementCostItem]
    summary: AnalyticsSummary