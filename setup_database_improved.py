import os
import logging
import argparse
from dotenv import load_dotenv

# Import custom modules
from supabase_client import get_supabase_client
from os_construction_manager import OSConstructionManager
from exceptions import DatabaseError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('setup_database.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_database(sample_data=False):
    """Set up the OSConstruction database.
    
    Args:
        sample_data (bool): Whether to create sample data
        
    Returns:
        bool: True if successful
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize the manager
        manager = OSConstructionManager()
        
        # Create database tables
        logger.info("Creating database tables...")
        manager.setup_database()
        logger.info("Database tables created successfully!")
        
        # Create sample data if requested
        if sample_data:
            logger.info("Creating sample data...")
            create_sample_data(manager)
            logger.info("Sample data created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False

def create_sample_data(manager):
    """Create sample data in the database.
    
    Args:
        manager: OSConstructionManager instance
    """
    try:
        # Add sample companies
        companies = [
            {
                "company_name": "OSConstruction Free Services",
                "company_address": "456 Builder Boulevard, Community City, CC 54321",
                "company_email": "contact@osconstructionfree.example.org",
                "company_phone": "+1-555-789-0123",
                "website": "https://osconstructionfree.example.org",
                "description": "Providing free construction services to underserved communities",
                "founded_year": 2020,
                "is_verified": True
            },
            {
                "company_name": "Community Builders Alliance",
                "company_address": "789 Helper Street, Volunteer Valley, VV 98765",
                "company_email": "info@communitybuilders.example.org",
                "company_phone": "+1-555-456-7890",
                "website": "https://communitybuilders.example.org",
                "description": "A network of volunteer builders helping low-income families",
                "founded_year": 2018,
                "is_verified": True
            },
            {
                "company_name": "Rebuild Together",
                "company_address": "321 Unity Road, Collaboration City, CC 45678",
                "company_email": "hello@rebuildtogether.example.org",
                "company_phone": "+1-555-234-5678",
                "website": "https://rebuildtogether.example.org",
                "description": "Collaborative construction efforts for disaster recovery",
                "founded_year": 2019,
                "is_verified": False
            }
        ]
        
        company_ids = []
        for company_data in companies:
            company = manager.add_company(company_data)
            company_ids.append(company["id"])
            logger.info(f"Added company: {company['company_name']} with ID: {company['id']}")
            
            # Add services for each company
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
                },
                {
                    "service_name": "Community Facilities",
                    "description": "Building and renovating community centers, parks, and public spaces",
                    "is_free": True,
                    "eligibility_criteria": "Must be a registered non-profit or community organization"
                }
            ]
            
            for service_data in services:
                service = manager.add_service(service_data, company["id"])
                logger.info(f"Added service: {service['service_name']} to company: {company['company_name']}")
            
            # Add projects for each company
            projects = [
                {
                    "project_name": "Community Center Renovation",
                    "location": "Downtown Community City",
                    "start_date": "2025-04-15",
                    "end_date": "2025-06-30",
                    "status": "planned",
                    "description": "Renovating the community center to provide better facilities",
                    "beneficiary_info": "Local community organizations and residents"
                },
                {
                    "project_name": "Senior Housing Repairs",
                    "location": "Elderly Estates, Volunteer Valley",
                    "start_date": "2025-03-01",
                    "end_date": "2025-05-15",
                    "status": "in_progress",
                    "description": "Repairing and upgrading housing for senior citizens",
                    "beneficiary_info": "Senior residents of Elderly Estates"
                },
                {
                    "project_name": "Playground Installation",
                    "location": "Family Park, Collaboration City",
                    "start_date": "2025-05-10",
                    "end_date": "2025-05-25",
                    "status": "planned",
                    "description": "Installing new playground equipment for children",
                    "beneficiary_info": "Local families and children"
                }
            ]
            
            for project_data in projects:
                project = manager.add_project(project_data, company["id"])
                logger.info(f"Added project: {project['project_name']} to company: {company['company_name']}")
            
            # Add employees for each company
            employees = [
                {
                    "full_name": "John Builder",
                    "position": "Construction Manager",
                    "email": "john@example.org",
                    "phone": "+1-555-111-2222",
                    "specialization": "Project Management",
                    "join_date": "2020-01-15"
                },
                {
                    "full_name": "Sarah Carpenter",
                    "position": "Lead Carpenter",
                    "email": "sarah@example.org",
                    "phone": "+1-555-333-4444",
                    "specialization": "Woodworking",
                    "join_date": "2020-02-01"
                },
                {
                    "full_name": "Michael Electrician",
                    "position": "Senior Electrician",
                    "email": "michael@example.org",
                    "phone": "+1-555-555-6666",
                    "specialization": "Electrical Systems",
                    "join_date": "2020-03-10"
                },
                {
                    "full_name": "Jessica Plumber",
                    "position": "Plumbing Expert",
                    "email": "jessica@example.org",
                    "phone": "+1-555-777-8888",
                    "specialization": "Plumbing",
                    "join_date": "2020-04-05"
                }
            ]
            
            for employee_data in employees:
                employee = manager.add_employee(employee_data, company["id"])
                logger.info(f"Added employee: {employee['full_name']} to company: {company['company_name']}")
        
        return company_ids
            
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        raise DatabaseError(f"Failed to create sample data: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set up the OSConstruction database')
    parser.add_argument('--sample', action='store_true', help='Create sample data')
    
    args = parser.parse_args()
    
    if setup_database(args.sample):
        print("Database setup completed successfully!")
        if args.sample:
            print("Sample data has been created.")
    else:
        print("Database setup failed. Check the logs for details.")