import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from osconstruction import create_client, Client

class OSConstructionManager:
    def __init__(self):
        self.supabase = self._initialize_supabase()
        
    def _initialize_supabase(self) -> Client:
        """Initialize the Supabase client."""
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
        
        return create_client(supabase_url, supabase_key)
    
    def setup_database(self) -> None:
        """Create necessary tables for OSConstruction if they don't exist."""
        # Create main company table
        self._create_company_table()
        
        # Create related tables for services, projects, and employees
        self._create_services_table()
        self._create_projects_table()
        self._create_employees_table()
        
        print("Database setup completed successfully!")
    
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
    def add_company(self, company_data: Dict[str, Any]) -> Dict:
        """Add a new construction company."""
        response = self.supabase.table("os_construction").insert(company_data).execute()
        return response.data[0] if response.data else {}
    
    def update_company(self, company_id: str, company_data: Dict[str, Any]) -> Dict:
        """Update an existing construction company."""
        company_data["updated_at"] = datetime.now().isoformat()
        response = self.supabase.table("os_construction").update(company_data).eq("id", company_id).execute()
        return response.data[0] if response.data else {}
    
    def get_company(self, company_id: str) -> Dict:
        """Get a company by ID."""
        response = self.supabase.table("os_construction").select("*").eq("id", company_id).execute()
        return response.data[0] if response.data else {}
    
    def get_all_companies(self) -> List[Dict]:
        """Get all construction companies."""
        response = self.supabase.table("os_construction").select("*").execute()
        return response.data if response.data else []
    
    def delete_company(self, company_id: str) -> bool:
        """Delete a company by ID."""
        response = self.supabase.table("os_construction").delete().eq("id", company_id).execute()
        return bool(response.data)
    
    # Service management methods
    def add_service(self, service_data: Dict[str, Any]) -> Dict:
        """Add a new service."""
        response = self.supabase.table("os_construction_services").insert(service_data).execute()
        return response.data[0] if response.data else {}
    
    def get_company_services(self, company_id: str) -> List[Dict]:
        """Get all services for a specific company."""
        response = self.supabase.table("os_construction_services").select("*").eq("company_id", company_id).execute()
        return response.data if response.data else []
    
    # Project management methods
    def add_project(self, project_data: Dict[str, Any]) -> Dict:
        """Add a new project."""
        response = self.supabase.table("os_construction_projects").insert(project_data).execute()
        return response.data[0] if response.data else {}
    
    def get_company_projects(self, company_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all projects for a specific company, optionally filtered by status."""
        query = self.supabase.table("os_construction_projects").select("*").eq("company_id", company_id)
        
        if status:
            query = query.eq("status", status)
            
        response = query.execute()
        return response.data if response.data else []
    
    # Employee management methods
    def add_employee(self, employee_data: Dict[str, Any]) -> Dict:
        """Add a new employee."""
        response = self.supabase.table("os_construction_employees").insert(employee_data).execute()
        return response.data[0] if response.data else {}
    
    def get_company_employees(self, company_id: str) -> List[Dict]:
        """Get all employees for a specific company."""
        response = self.supabase.table("os_construction_employees").select("*").eq("company_id", company_id).execute()
        return response.data if response.data else []

# Example usage
if __name__ == "__main__":
    try:
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
        print(f"Added company: {company['company_name']} with ID: {company['id']}")
        
        # Add services for the company
        services = [
            {
                "company_id": company["id"],
                "service_name": "Home Repairs",
                "description": "Basic home repairs for elderly and disabled individuals",
                "is_free": True,
                "eligibility_criteria": "Must be 65+ or have a disability, income below poverty line"
            },
            {
                "company_id": company["id"],
                "service_name": "Disaster Recovery",
                "description": "Rebuilding assistance after natural disasters",
                "is_free": True,
                "eligibility_criteria": "Must be affected by a declared natural disaster"
            }
        ]
        
        for service_data in services:
            service = manager.add_service(service_data)
            print(f"Added service: {service['service_name']}")
        
        # Add a project
        project_data = {
            "company_id": company["id"],
            "project_name": "Community Center Renovation",
            "location": "Downtown Community City",
            "start_date": "2025-04-15",
            "end_date": "2025-06-30",
            "status": "planned",
            "description": "Renovating the community center to provide better facilities",
            "beneficiary_info": "Local community organizations and residents"
        }
        project = manager.add_project(project_data)
        print(f"Added project: {project['project_name']}")
        
        # Get company with all related data
        print("\nCompany Information:")
        retrieved_company = manager.get_company(company["id"])
        print(f"Name: {retrieved_company['company_name']}")
        print(f"Contact: {retrieved_company['company_email']}")
        
        print("\nServices Offered:")
        company_services = manager.get_company_services(company["id"])
        for service in company_services:
            print(f"- {service['service_name']}: {service['description']}")
        
        print("\nProjects:")
        company_projects = manager.get_company_projects(company["id"])
        for project in company_projects:
            print(f"- {project['project_name']} ({project['status']}): {project['description']}")
        
    except Exception as e:
        print(f"Error: {e}")