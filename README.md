# OSConstruction Database System

A comprehensive database and API system for managing OSConstruction, a free construction services organization.

## Overview

This project provides a complete solution for managing construction companies that offer free services, their projects, service offerings, and employees. It includes:

1. A Supabase database setup
2. Python client library
3. REST API with Flask

## Features

- **Company Management**: Store and manage construction company details
- **Services Tracking**: Document the free services offered
- **Project Management**: Track ongoing and completed construction projects
- **Employee Directory**: Maintain records of staff and volunteers
- **API Access**: RESTful API for integration with other systems

## Getting Started

### Prerequisites

- Python 3.8+
- [Supabase](https://supabase.io/) account
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/os-construction-db.git
cd os-construction-db
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Database Setup

Run the database setup script to create the necessary tables:

```bash
python setup_database.py
```

This will create the following tables:
- `os_construction` - Main company information
- `os_construction_services` - Services offered
- `os_construction_projects` - Construction projects
- `os_construction_employees` - Staff records

## Usage

### Python Library

```python
from os_construction import OSConstructionManager

# Initialize the manager
manager = OSConstructionManager()

# Add a new construction company
company_data = {
    "company_name": "Build Better Communities",
    "company_address": "123 Main St, Anytown, USA",
    "company_email": "info@buildbetter.org",
    "company_phone": "+1-555-123-4567"
}
company = manager.add_company(company_data)

# Add a service
service_data = {
    "company_id": company["id"],
    "service_name": "Home Repairs for Seniors",
    "description": "Free home repair services for seniors",
    "is_free": True,
    "eligibility_criteria": "65+ years old"
}
manager.add_service(service_data)

# Get all companies
companies = manager.get_all_companies()
```

### REST API

Start the API server:

```bash
python app.py
```

#### Available Endpoints:

**Companies:**
- `GET /api/companies` - List all companies
- `GET /api/companies/{id}` - Get a specific company
- `POST /api/companies` - Create a new company
- `PUT /api/companies/{id}` - Update a company
- `DELETE /api/companies/{id}` - Delete a company

**Services:**
- `GET /api/companies/{id}/services` - List services for a company
- `POST /api/companies/{id}/services` - Add a service to a company

**Projects:**
- `GET /api/companies/{id}/projects` - List projects for a company
- `POST /api/companies/{id}/projects` - Add a project to a company

**Employees:**
- `GET /api/companies/{id}/employees` - List employees for a company
- `POST /api/companies/{id}/employees` - Add an employee to a company

## API Examples

### Create a Company

```bash
curl -X POST http://localhost:5000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Community Builders",
    "company_address": "456 Oak St, Cityville, USA",
    "company_email": "contact@communitybuilders.org",
    "company_phone": "+1-555-987-6543",
    "website": "https://communitybuilders.org",
    "description": "Building better communities through service"
  }'
```

### Get Company Services

```bash
curl -X GET http://localhost:5000/api/companies/YOUR_COMPANY_ID/services
```

### Add a Project

```bash
curl -X POST http://localhost:5000/api/companies/YOUR_COMPANY_ID/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Community Center Renovation",
    "location": "Downtown Commons",
    "start_date": "2025-05-01",
    "end_date": "2025-07-15",
    "status": "planned",
    "description": "Renovating the community center"
  }'
```

## Database Schema

### os_construction (Companies)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_name | VARCHAR(255) | Name of the company |
| company_address | TEXT | Physical address |
| company_email | VARCHAR(255) | Contact email |
| company_phone | VARCHAR(50) | Contact phone number |
| website | VARCHAR(255) | Company website URL |
| description | TEXT | Company description |
| founded_year | INT | Year founded |
| is_verified | BOOLEAN | Verification status |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Record update time |

### os_construction_services (Services)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key to company |
| service_name | VARCHAR(255) | Name of service |
| description | TEXT | Service description |
| is_free | BOOLEAN | Whether service is free |
| eligibility_criteria | TEXT | Who qualifies for service |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Record update time |

### os_construction_projects (Projects)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key to company |
| project_name | VARCHAR(255) | Project name |
| location | TEXT | Project location |
| start_date | DATE | Start date |
| end_date | DATE | Completion date |
| status | VARCHAR(50) | Project status |
| description | TEXT | Project description |
| beneficiary_info | TEXT | Who benefits |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Record update time |

### os_construction_employees (Employees)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key to company |
| full_name | VARCHAR(255) | Employee name |
| position | VARCHAR(100) | Job title |
| email | VARCHAR(255) | Contact email |
| phone | VARCHAR(50) | Contact phone |
| specialization | VARCHAR(100) | Area of expertise |
| join_date | DATE | When they joined |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Record update time |

## Project Structure

```
os-construction-db/
├── app.py                  # Flask API
├── setup_database.py       # Database setup script
├── os_construction.py      # Python library
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact [your-email@example.com].