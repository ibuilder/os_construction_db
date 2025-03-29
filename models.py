from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime


class CompanyBase(BaseModel):
    """Base model for company data with validation."""
    company_name: str = Field(..., min_length=1, max_length=255)
    company_address: str
    company_email: EmailStr
    company_phone: str = Field(..., min_length=5, max_length=50)


class CompanyCreate(CompanyBase):
    """Model for creating a new company."""
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    is_verified: bool = False

    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v


class CompanyUpdate(BaseModel):
    """Model for updating an existing company."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_address: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone: Optional[str] = Field(None, min_length=5, max_length=50)
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    is_verified: Optional[bool] = None

    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v


class CompanyResponse(CompanyBase):
    """Model for company response data."""
    id: str
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class ServiceBase(BaseModel):
    """Base model for service data with validation."""
    service_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_free: bool = True
    eligibility_criteria: Optional[str] = None


class ServiceCreate(ServiceBase):
    """Model for creating a new service."""
    pass


class ServiceUpdate(BaseModel):
    """Model for updating an existing service."""
    service_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_free: Optional[bool] = None
    eligibility_criteria: Optional[str] = None


class ServiceResponse(ServiceBase):
    """Model for service response data."""
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime


class ProjectBase(BaseModel):
    """Base model for project data with validation."""
    project_name: str = Field(..., min_length=1, max_length=255)
    location: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planned"
    description: Optional[str] = None
    beneficiary_info: Optional[str] = None

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'on_hold']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None
    beneficiary_info: Optional[str] = None

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'on_hold']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class ProjectResponse(ProjectBase):
    """Model for project response data."""
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime


class EmployeeBase(BaseModel):
    """Base model for employee data with validation."""
    full_name: str = Field(..., min_length=1, max_length=255)
    position: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    join_date: Optional[date] = None


class EmployeeCreate(EmployeeBase):
    """Model for creating a new employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Model for updating an existing employee."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    join_date: Optional[date] = None


class EmployeeResponse(EmployeeBase):
    """Model for employee response data."""
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    """Generic model for paginated responses."""
    data: List
    pagination: dict