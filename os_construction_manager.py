import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

# Import custom modules
from supabase_client import get_supabase_client
from exceptions import (ResourceNotFoundError, ValidationError, 
                       DatabaseConnectionError, DatabaseError)
from models import (CompanyCreate, CompanyUpdate, ServiceCreate, 
                   ProjectCreate, EmployeeCreate)

logger = logging.getLogger(__name__)

class OSConstructionManager:
    """Manager class for OSConstruction database operations.
    
    This class provides methods for interacting with the OSConstruction
    database, including CRUD operations for companies, services, projects,
    and employees.
    """
    
    def __init__(self):
        """Initialize the OSConstructionManager."""
        self.supabase = get_supabase_client()
    
    def setup_database(self) -> None:
        """Create necessary tables for OSConstruction if they don't exist."""
        try:
            # Create main company table
            self._create_company_table()
            
            # Create related tables for services, projects, and employees
            self._create_services_table()
            self._create_projects_table()
            self._create_employees_table()
            
            logger.info("Database setup completed successfully!")
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise DatabaseError(f"Failed to set up database: {str(e)}")
    
    def _create_company_table(self) -> None:
        """Create the company table."""
        sql = """
        CREATE TABLE IF NOT EXISTS os_construction (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_name VARCHAR(255) NOT NULL,
            company_address TEXT NOT NULL,
            company_email VARCHAR(255) NOT NULL,
            company_phone VARCHAR(50) NOT NULL,
            website VARCHAR(255),
            description TEXT,
            founded_year INT,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        self.supabase.table("os_construction").execute(sql)
    
    def _create_services_table(self) -> None:
        """Create the services table."""
        sql = """
        CREATE TABLE IF NOT EXISTS os_construction_services (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES os_construction(id) ON DELETE CASCADE,
            service_name VARCHAR(255) NOT NULL,
            description TEXT,
            is_free BOOLEAN DEFAULT TRUE,
            eligibility_criteria TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        self.supabase.table("os_construction_services").execute(sql)
    
    def _create_projects_table(self) -> None:
        """Create the projects table."""
        sql = """
        CREATE TABLE IF NOT EXISTS os_construction_projects (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES os_construction(id) ON DELETE CASCADE,
            project_name VARCHAR(255) NOT NULL,
            location TEXT NOT NULL,
            start_date DATE,
            end_date DATE,
            status VARCHAR(50) DEFAULT 'planned',
            description TEXT,
            beneficiary_info TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        self.supabase.table("os_construction_projects").execute(sql)
    
    def _create_employees_table(self) -> None:
        """Create the employees table."""
        sql = """
        CREATE TABLE IF NOT EXISTS os_construction_employees (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES os_construction(id) ON DELETE CASCADE,
            full_name VARCHAR(255) NOT NULL,
            position VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            specialization VARCHAR(100),
            join_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        self.supabase.table("os_construction_employees").execute(sql)
    
    # Company management methods
    def add_company(self, company_data: Union[Dict[str, Any], CompanyCreate]) -> Dict:
        """Add a new construction company.
        
        Args:
            company_data: Company data as a dict or CompanyCreate instance
            
        Returns:
            Dict: The created company record
            
        Raises:
            ValidationError: If the data is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Handle both dict and Pydantic model inputs
            if isinstance(company_data, CompanyCreate):
                db_data = company_data.dict()
            else:
                # Validate with Pydantic model
                validated_data = CompanyCreate(**company_data)
                db_data = validated_data.dict()
            
            # Add timestamps
            now = datetime.now().isoformat()
            db_data["created_at"] = now
            db_data["updated_at"] = now
            
            response = self.supabase.table("os_construction").insert(db_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create company")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding company: {e}")
            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to add company: {str(e)}")
    
    def update_company(self, company_id: str, company_data: Union[Dict[str, Any], CompanyUpdate]) -> Dict:
        """Update an existing construction company.
        
        Args:
            company_id: The ID of the company to update
            company_data: The updated company data
            
        Returns:
            Dict: The updated company record
            
        Raises:
            ResourceNotFoundError: If the company is not found
            ValidationError: If the data is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Handle both dict and Pydantic model inputs
            if isinstance(company_data, CompanyUpdate):
                # Convert to dict and remove None values
                db_data = {k: v for k, v in company_data.dict().items() if v is not None}
            else:
                # Validate with Pydantic model
                validated_data = CompanyUpdate(**company_data)
                db_data = {k: v for k, v in validated_data.dict().items() if v is not None}
            
            # Add updated timestamp
            db_data["updated_at"] = datetime.now().isoformat()
            
            response = self.supabase.table("os_construction").update(db_data).eq("id", company_id).execute()
            
            if not response.data:
                raise DatabaseError("Failed to update company")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating company {company_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to update company: {str(e)}")
    
    def get_company(self, company_id: str) -> Dict:
        """Get a company by ID.
        
        Args:
            company_id: The ID of the company to retrieve
            
        Returns:
            Dict: The company record
            
        Raises:
            ResourceNotFoundError: If the company is not found
            DatabaseError: If the database operation fails
        """
        try:
            response = self.supabase.table("os_construction").select("*").eq("id", company_id).execute()
            
            if not response.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error getting company {company_id}: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise
            raise DatabaseError(f"Failed to retrieve company: {str(e)}")
    
    def get_all_companies(self, page: int = 1, per_page: int = 10, 
                         is_verified: Optional[bool] = None, 
                         name_search: Optional[str] = None) -> Dict:
        """Get all construction companies with pagination and filtering.
        
        Args:
            page: Page number (starts at 1)
            per_page: Number of items per page
            is_verified: Filter by verification status
            name_search: Filter by company name (partial match)
            
        Returns:
            Dict: Paginated response with company records
            
        Raises:
            DatabaseError: If the database operation fails
        """
        try:
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Build query
            query = self.supabase.table("os_construction_projects").select("*").eq("company_id", company_id)
            
            if status:
                query = query.eq("status", status)
            
            # Get total count (filtered)
            count_response = query.execute()
            total_count = len(count_response.data)
            
            # Apply pagination
            query = query.range(offset, offset + per_page - 1)
            response = query.execute()
            
            # Return paginated response
            return {
                "data": response.data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page if total_count > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting projects for company {company_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, ValidationError)):
                raise
            raise DatabaseError(f"Failed to retrieve projects: {str(e)}")
    
    # Employee management methods
    def add_employee(self, employee_data: Union[Dict[str, Any], EmployeeCreate], company_id: str) -> Dict:
        """Add a new employee for a company.
        
        Args:
            employee_data: Employee data
            company_id: The ID of the company to add the employee to
            
        Returns:
            Dict: The created employee record
            
        Raises:
            ResourceNotFoundError: If the company is not found
            ValidationError: If the data is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Handle both dict and Pydantic model inputs
            if isinstance(employee_data, EmployeeCreate):
                db_data = employee_data.dict()
            else:
                # Validate with Pydantic model
                validated_data = EmployeeCreate(**employee_data)
                db_data = validated_data.dict()
            
            # Add company ID
            db_data["company_id"] = company_id
            
            # Handle date field - convert to ISO format string
            if db_data.get("join_date"):
                db_data["join_date"] = db_data["join_date"].isoformat()
            
            # Add timestamps
            now = datetime.now().isoformat()
            db_data["created_at"] = now
            db_data["updated_at"] = now
            
            response = self.supabase.table("os_construction_employees").insert(db_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create employee")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding employee for company {company_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to add employee: {str(e)}")
    
    def get_company_employees(self, company_id: str, page: int = 1, per_page: int = 10) -> Dict:
        """Get all employees for a specific company with pagination.
        
        Args:
            company_id: The ID of the company
            page: Page number (starts at 1)
            per_page: Number of items per page
            
        Returns:
            Dict: Paginated response with employee records
            
        Raises:
            ResourceNotFoundError: If the company is not found
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Get total count
            count_query = self.supabase.table("os_construction_employees").select("count", count="exact").eq("company_id", company_id)
            count_response = count_query.execute()
            total_count = count_response.count if hasattr(count_response, 'count') else 0
            
            # Get employees with pagination
            query = self.supabase.table("os_construction_employees").select("*").eq("company_id", company_id)
            query = query.range(offset, offset + per_page - 1)
            response = query.execute()
            
            # Return paginated response
            return {
                "data": response.data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page if total_count > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting employees for company {company_id}: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise
            raise DatabaseError(f"Failed to retrieve employees: {str(e)}")
    
    # Advanced methods
    def transfer_employee(self, employee_id: str, from_company_id: str, to_company_id: str) -> bool:
        """Transfer an employee from one company to another using a transaction.
        
        Args:
            employee_id: The ID of the employee to transfer
            from_company_id: The ID of the current company
            to_company_id: The ID of the destination company
            
        Returns:
            bool: True if successful
            
        Raises:
            ResourceNotFoundError: If the employee or companies are not found
            DatabaseError: If the database operation fails
        """
        try:
            # Check if employee exists in the first company
            employee_check = self.supabase.table("os_construction_employees").select("*").eq("id", employee_id).eq("company_id", from_company_id).execute()
            
            if not employee_check.data:
                raise ResourceNotFoundError(f"Employee with ID {employee_id} not found in company {from_company_id}")
            
            # Check if destination company exists
            company_check = self.supabase.table("os_construction").select("id").eq("id", to_company_id).execute()
            
            if not company_check.data:
                raise ResourceNotFoundError(f"Destination company with ID {to_company_id} not found")
            
            # Get employee data
            employee_data = employee_check.data[0]
            
            # Create transaction function
            # Note: This is a simplified version since Supabase doesn't directly support transactions through the API
            # In a real application, you would create a PostgreSQL function for this
            
            # Update employee record
            update_data = {
                "company_id": to_company_id,
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table("os_construction_employees").update(update_data).eq("id", employee_id).execute()
            
            if not response.data:
                raise DatabaseError("Failed to transfer employee")
                
            return True
        except Exception as e:
            logger.error(f"Error transferring employee {employee_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to transfer employee: {str(e)}")
    
    def get_company_summary(self, company_id: str) -> Dict:
        """Get a summary of a company with counts of services, projects, and employees.
        
        Args:
            company_id: The ID of the company
            
        Returns:
            Dict: Company summary with counts
            
        Raises:
            ResourceNotFoundError: If the company is not found
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists and get company data
            company = self.get_company(company_id)
            
            # Get counts
            services_count = len(self.supabase.table("os_construction_services").select("id").eq("company_id", company_id).execute().data)
            
            projects_query = self.supabase.table("os_construction_projects").select("id", "status").eq("company_id", company_id).execute()
            projects = projects_query.data
            projects_count = len(projects)
            
            # Count projects by status
            project_status_counts = {}
            for project in projects:
                status = project.get("status", "unknown")
                project_status_counts[status] = project_status_counts.get(status, 0) + 1
            
            employees_count = len(self.supabase.table("os_construction_employees").select("id").eq("company_id", company_id).execute().data)
            
            # Construct summary
            summary = {
                "company": company,
                "counts": {
                    "services": services_count,
                    "projects": {
                        "total": projects_count,
                        "by_status": project_status_counts
                    },
                    "employees": employees_count
                }
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error getting summary for company {company_id}: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise
            raise DatabaseError(f"Failed to retrieve company summary: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('os_construction_manager.log')
            ]
        )
        
        manager = OSConstructionManager()
        
        # Set up the database structure
        manager.setup_database()
        
        # Add a new construction company
        company_data = {
            "company_name": "OSConstruction Free Services",
            "company_address": "456 Builder Boulevard, Community City, CC 54321",
            "company_email": "contact@osconstructionfree.example.org",
            "company_phone": "+1-555-789-0123",
            "website": "https://osconstructionfree.example.org",
            "description": "Providing free construction services to underserved communities",
            "founded_year": 2020,
            "is_verified": True
        }
        company = manager.add_company(company_data)
        logger.info(f"Added company: {company['company_name']} with ID: {company['id']}")
        
        # Add services for the company
        services = [
            {
                "service_name": "Home Repairs",
                "description": "Basic home repairs for elderly and disabled individuals",
                "is_free": True,
                "eligibility_criteria": "Must be 65+ or have a disability, income below poverty line"
            },
            {
                "service_name": "Disaster Recovery",
                "description": "Rebuilding assistance after natural disasters",
                "is_free": True,
                "eligibility_criteria": "Must be affected by a declared natural disaster"
            }
        ]
        
        for service_data in services:
            service = manager.add_service(service_data, company["id"])
            logger.info(f"Added service: {service['service_name']}")
        
        # Add a project
        project_data = {
            "project_name": "Community Center Renovation",
            "location": "Downtown Community City",
            "start_date": "2025-04-15",
            "end_date": "2025-06-30",
            "status": "planned",
            "description": "Renovating the community center to provide better facilities",
            "beneficiary_info": "Local community organizations and residents"
        }
        project = manager.add_project(project_data, company["id"])
        logger.info(f"Added project: {project['project_name']}")
        
        # Get company summary
        summary = manager.get_company_summary(company["id"])
        logger.info(f"Company Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Error in example: {e}")

            # Build query
            query = self.supabase.table("os_construction").select("*")
            
            # Apply filters
            if is_verified is not None:
                query = query.eq("is_verified", is_verified)
                
            if name_search:
                query = query.ilike("company_name", f"%{name_search}%")
            
            # Get total count
            count_query = query
            count_response = count_query.execute()
            total_count = len(count_response.data)
            
            # Apply pagination
            query = query.range(offset, offset + per_page - 1)
            response = query.execute()
            
            # Return paginated response
            return {
                "data": response.data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page if total_count > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting all companies: {e}")
            raise DatabaseError(f"Failed to retrieve companies: {str(e)}")
    
    def delete_company(self, company_id: str) -> bool:
        """Delete a company by ID.
        
        Args:
            company_id: The ID of the company to delete
            
        Returns:
            bool: True if successful
            
        Raises:
            ResourceNotFoundError: If the company is not found
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            response = self.supabase.table("os_construction").delete().eq("id", company_id).execute()
            
            if not response.data:
                raise DatabaseError("Failed to delete company")
                
            return True
        except Exception as e:
            logger.error(f"Error deleting company {company_id}: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise
            raise DatabaseError(f"Failed to delete company: {str(e)}")
    
    # Service management methods
    def add_service(self, service_data: Union[Dict[str, Any], ServiceCreate], company_id: str) -> Dict:
        """Add a new service for a company.
        
        Args:
            service_data: Service data
            company_id: The ID of the company to add the service to
            
        Returns:
            Dict: The created service record
            
        Raises:
            ResourceNotFoundError: If the company is not found
            ValidationError: If the data is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Handle both dict and Pydantic model inputs
            if isinstance(service_data, ServiceCreate):
                db_data = service_data.dict()
            else:
                # Validate with Pydantic model
                validated_data = ServiceCreate(**service_data)
                db_data = validated_data.dict()
            
            # Add company ID and timestamps
            db_data["company_id"] = company_id
            now = datetime.now().isoformat()
            db_data["created_at"] = now
            db_data["updated_at"] = now
            
            response = self.supabase.table("os_construction_services").insert(db_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create service")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding service for company {company_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to add service: {str(e)}")
    
    def get_company_services(self, company_id: str, page: int = 1, per_page: int = 10) -> Dict:
        """Get all services for a specific company with pagination.
        
        Args:
            company_id: The ID of the company
            page: Page number (starts at 1)
            per_page: Number of items per page
            
        Returns:
            Dict: Paginated response with service records
            
        Raises:
            ResourceNotFoundError: If the company is not found
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Get total count
            count_query = self.supabase.table("os_construction_services").select("count", count="exact").eq("company_id", company_id)
            count_response = count_query.execute()
            total_count = count_response.count if hasattr(count_response, 'count') else 0
            
            # Get services with pagination
            query = self.supabase.table("os_construction_services").select("*").eq("company_id", company_id)
            query = query.range(offset, offset + per_page - 1)
            response = query.execute()
            
            # Return paginated response
            return {
                "data": response.data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page if total_count > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting services for company {company_id}: {e}")
            if isinstance(e, ResourceNotFoundError):
                raise
            raise DatabaseError(f"Failed to retrieve services: {str(e)}")
    
    # Project management methods
    def add_project(self, project_data: Union[Dict[str, Any], ProjectCreate], company_id: str) -> Dict:
        """Add a new project for a company.
        
        Args:
            project_data: Project data
            company_id: The ID of the company to add the project to
            
        Returns:
            Dict: The created project record
            
        Raises:
            ResourceNotFoundError: If the company is not found
            ValidationError: If the data is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Handle both dict and Pydantic model inputs
            if isinstance(project_data, ProjectCreate):
                db_data = project_data.dict()
            else:
                # Validate with Pydantic model
                validated_data = ProjectCreate(**project_data)
                db_data = validated_data.dict()
            
            # Add company ID
            db_data["company_id"] = company_id
            
            # Handle date fields - convert to ISO format strings
            if db_data.get("start_date"):
                db_data["start_date"] = db_data["start_date"].isoformat()
            if db_data.get("end_date"):
                db_data["end_date"] = db_data["end_date"].isoformat()
            
            # Add timestamps
            now = datetime.now().isoformat()
            db_data["created_at"] = now
            db_data["updated_at"] = now
            
            response = self.supabase.table("os_construction_projects").insert(db_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create project")
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding project for company {company_id}: {e}")
            if isinstance(e, (ResourceNotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"Failed to add project: {str(e)}")
    
    def get_company_projects(self, company_id: str, status: Optional[str] = None, 
                           page: int = 1, per_page: int = 10) -> Dict:
        """Get all projects for a specific company with filtering and pagination.
        
        Args:
            company_id: The ID of the company
            status: Filter by project status
            page: Page number (starts at 1)
            per_page: Number of items per page
            
        Returns:
            Dict: Paginated response with project records
            
        Raises:
            ResourceNotFoundError: If the company is not found
            ValidationError: If status is invalid
            DatabaseError: If the database operation fails
        """
        try:
            # Check if company exists
            check = self.supabase.table("os_construction").select("id").eq("id", company_id).execute()
            if not check.data:
                raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
            # Validate status if provided
            if status:
                valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'on_hold']
                if status not in valid_statuses:
                    raise ValidationError(f"Invalid status. Must be one of {valid_statuses}")
            
            # Calculate offset for pagination
            offset = (page - 1) * per_page