
from pydantic import BaseModel, Field
from typing import List, Literal
from app.schemas.enums import DepartmentType

# ==============================================================================
# ENPOINT 1: /api/analytics/department-costs
# ==============================================================================

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


# ==============================================================================
# ENDPOINT 2: /api/analytics/expensive-tools (Le petit nouveau)
# ==============================================================================

class ExpensiveToolsParams(BaseModel):
    limit: int = Field(10, ge=1, le=100, description="Nombre maximum d'outils à retourner")
    min_cost: float = Field(0.0, ge=0.0, description="Filtre sur le coût mensuel minimum")

class ToolCostDetail(BaseModel):
    id: int
    name: str
    monthly_cost: float
    active_users_count: int
    cost_per_user: float
    department: DepartmentType
    vendor: str
    efficiency_rating: Literal["excellent", "good", "average", "low"]

class AnalyticsExpensiveToolsSummary(BaseModel):
    total_tools_analyzed: int
    avg_cost_per_user_company: float
    potential_savings_identified: float

class ExpensiveToolsResponse(BaseModel):
    data: List[ToolCostDetail]
    analysis: AnalyticsExpensiveToolsSummary