from pydantic import BaseModel, Field
from typing import List, Literal, Optional
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
    message: Optional[str] = None


# ==============================================================================
# ENDPOINT 2: /api/analytics/expensive-tools
# ==============================================================================


class ExpensiveToolsParams(BaseModel):
    limit: int = Field(
        10, ge=1, le=100, description="Nombre maximum d'outils à retourner"
    )
    min_cost: float = Field(
        0.0, ge=0.0, description="Filtre sur le coût mensuel minimum"
    )


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


# ==============================================================================
# ENDPOINT 3: /api/analytics/tools-by-category (Répartition catégories)
# ==============================================================================


class CategoryCostDetail(BaseModel):
    category_name: str
    tools_count: int
    total_cost: float
    total_users: int
    percentage_of_budget: float
    average_cost_per_user: float


class AnalyticsCategoryInsights(BaseModel):
    most_expensive_category: str
    most_efficient_category: str


class ToolsByCategoryResponse(BaseModel):
    data: List[CategoryCostDetail]
    insights: AnalyticsCategoryInsights


# ==============================================================================
# ENDPOINT 4: /api/analytics/low-usage-tools (Outils sous-utilisés)
# ==============================================================================


class LowUsageToolDetail(BaseModel):
    id: int
    name: str
    monthly_cost: float
    active_users_count: int
    cost_per_user: float
    department: DepartmentType
    vendor: str
    warning_level: Literal["high", "medium", "low"]
    potential_action: str


class AnalyticsSavingsAnalysis(BaseModel):
    total_underutilized_tools: int
    potential_monthly_savings: float
    potential_annual_savings: float


class LowUsageToolsResponse(BaseModel):
    data: List[LowUsageToolDetail]
    savings_analysis: AnalyticsSavingsAnalysis


# ==============================================================================
# ENDPOINT 5: /api/analytics/vendor-summary (Analyse fournisseurs)
# ==============================================================================


class VendorCostDetail(BaseModel):
    vendor: str
    tools_count: int
    total_monthly_cost: float
    total_users: int
    departments: str  # Chaîne concaténée, ex: "Engineering,Marketing,Sales"
    average_cost_per_user: float
    vendor_efficiency: Literal["excellent", "good", "average", "poor"]


class AnalyticsVendorInsights(BaseModel):
    most_expensive_vendor: str
    most_efficient_vendor: str
    single_tool_vendors: int


class VendorSummaryResponse(BaseModel):
    data: List[VendorCostDetail]
    vendor_insights: AnalyticsVendorInsights
