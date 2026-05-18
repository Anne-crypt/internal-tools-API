from enum import Enum


class DepartmentType(str, Enum):
    ENGINEERING = "Engineering"
    SALES = "Sales"
    MARKETING = "Marketing"
    HR = "HR"
    FINANCE = "Finance"
    OPERATIONS = "Operations"
    DESIGN = "Design"


class ToolStatusType(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    TRIAL = "trial"


class UserRoleType(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class UserStatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AccessStatusType(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class RequestStatusType(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"