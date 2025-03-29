from flask import Flask, request, jsonify
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from pydantic import ValidationError as PydanticValidationError

# Import custom modules
from config import get_config
from supabase_client import get_supabase_client
from exceptions import (OSConstructionError, DatabaseConnectionError, 
                       ResourceNotFoundError, ValidationError, 
                       AuthenticationError, AuthorizationError)
from models import (CompanyCreate, CompanyUpdate, ServiceCreate, 
                  ProjectCreate, EmployeeCreate, PaginatedResponse)
from authentication import token_required, admin_required, generate_token

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Setup CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[app.config.get('RATELIMIT_DEFAULT')],
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL')
)

# Configure logging
def setup_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler(
        app.config.get('LOG_FILE'), 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    file_handler.setLevel(log_level)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    app.logger.info('Application startup')

setup_logging()

# Error Handlers
@app.errorhandler(OSConstructionError)
def handle_custom_exception(e):
    if isinstance(e, ResourceNotFoundError):
        return jsonify({"error": "Not Found", "message": str(e)}), 404
    elif isinstance(e, ValidationError) or isinstance(e, PydanticValidationError):
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    elif isinstance(e, AuthenticationError):
        return jsonify({"error": "Authentication Error", "message": str(e)}), 401
    elif isinstance(e, AuthorizationError):
        return jsonify({"error": "Authorization Error", "message": str(e)}), 403
    elif isinstance(e, DatabaseConnectionError):
        return jsonify({"error": "Database Connection Error", "message": str(e)}), 503
    else:
        return jsonify({"error": "Application Error", "message": str(e)}), 500

@app.errorhandler(Exception)
def handle_generic_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

# Helper functions
def get_pagination_params():
    """Extract pagination parameters from request."""
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, min(100, int(request.args.get('per_page', 10))))
        return page, per_page
    except (ValueError, TypeError):
        raise ValidationError("Invalid pagination parameters")

def paginate_query(query, page, per_page):
    """Apply pagination to a Supabase query."""
    offset = (page - 1) * per_page
    return query.range(offset, offset + per_page - 1)

def get_total_count(supabase, table):
    """Get total count of records in a table."""
    try:
        response = supabase.table(table).select("count", count="exact").execute()
        return response.count if hasattr(response, 'count') else 0
    except Exception as e:
        app.logger.error(f"Error getting count from {table}: {e}")
        return 0

def format_paginated_response(data, page, per_page, total):
    """Format a paginated response."""
    return {
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page if total > 0 else 0
        }
    }

# Auth routes
@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return a JWT token.
    
    For this example, we're using a simplified authentication model.
    In a real application, you would verify against users in your database.
    """
    try:
        data = request.json
        
        if not data:
            raise ValidationError("No data provided")
            
        if not data.get('username') or not data.get('password'):
            raise ValidationError("Username and password are required")
        
        # For demo purposes, we're using hardcoded credentials
        # In a real app, you would verify against your database
        if data.get('username') == 'admin' and data.get('password') == 'password':
            # Generate JWT token
            token = generate_token(
                user_id="admin-user-id",
                username=data.get('username')
            )
            
            return jsonify({
                "token": token,
                "expires_in": app.config.get('JWT_ACCESS_TOKEN_EXPIRES'),
                "user": {
                    "id": "admin-user-id",
                    "username": data.get('username')
                }
            })
        
        raise AuthenticationError("Invalid credentials")
        
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        if isinstance(e, (ValidationError, AuthenticationError)):
            raise
        raise AuthenticationError("Authentication failed")

# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        supabase = get_supabase_client()
        supabase.table("os_construction").select("count", count="exact").limit(1).execute()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "environment": os.environ.get('FLASK_ENV', 'default')
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "environment": os.environ.get('FLASK_ENV', 'default')
        }), 500

# Company endpoints
@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Get all construction companies with pagination and filtering."""
    try:
        # Get pagination parameters
        page, per_page = get_pagination_params()
        
        # Get filter parameters
        is_verified = request.args.get('is_verified')
        name_search = request.args.get('name')
        
        # Initialize Supabase client
        supabase = get_supabase_client()
        query = supabase.table("os_construction").select("*")
        
        # Apply filters if provided
        if is_verified is not None:
            is_verified_bool = is_verified.lower() == 'true'
            query = query.eq("is_verified", is_verified_bool)
            
        if name_search:
            query = query.ilike("company_name", f"%{name_search}%")
        
        # Get total count for pagination metadata
        total_count = get_total_count(supabase, "os_construction")
        
        # Apply pagination
        query = paginate_query(query, page, per_page)
        
        # Execute the query
        response = query.execute()
        
        # Format and return the response
        result = format_paginated_response(response.data, page, per_page, total_count)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error fetching companies: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to retrieve companies: {str(e)}")

@app.route("/api/companies/<company_id>", methods=["GET"])
def get_company(company_id):
    """Get a specific company by ID."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("os_construction").select("*").eq("id", company_id).execute()
        
        if not response.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
            
        return jsonify(response.data[0])
    except Exception as e:
        app.logger.error(f"Error fetching company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to retrieve company: {str(e)}")

@app.route("/api/companies", methods=["POST"])
@token_required
@limiter.limit("10 per minute")
def create_company():
    """Create a new company with validated data."""
    try:
        # Parse and validate input data
        data = request.json
        if not data:
            raise ValidationError("No data provided")
        
        # Validate with Pydantic model
        company_data = CompanyCreate(**data)
        
        # Convert to dict for inserting to database
        db_data = company_data.dict()
        
        # Add timestamps
        now = datetime.datetime.utcnow().isoformat()
        db_data["created_at"] = now
        db_data["updated_at"] = now
        
        # Insert into database
        supabase = get_supabase_client()
        response = supabase.table("os_construction").insert(db_data).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to create company")
            
        return jsonify(response.data[0]), 201
        
    except PydanticValidationError as e:
        # Convert Pydantic validation error to our custom error
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise ValidationError(f"Invalid data: {'; '.join(error_messages)}")
        
    except Exception as e:
        app.logger.error(f"Error creating company: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to create company: {str(e)}")

@app.route("/api/companies/<company_id>", methods=["PUT"])
@token_required
def update_company(company_id):
    """Update an existing company."""
    try:
        data = request.json
        if not data:
            raise ValidationError("No data provided")
            
        # Validate with Pydantic model - partial update allowed
        company_data = CompanyUpdate(**data)
        
        # Convert to dict and remove None values
        db_data = {k: v for k, v in company_data.dict().items() if v is not None}
        
        # Add updated timestamp
        db_data["updated_at"] = datetime.datetime.utcnow().isoformat()
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        response = supabase.table("os_construction").update(db_data).eq("id", company_id).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to update company")
            
        return jsonify(response.data[0])
        
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise ValidationError(f"Invalid data: {'; '.join(error_messages)}")
        
    except Exception as e:
        app.logger.error(f"Error updating company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to update company: {str(e)}")

@app.route("/api/companies/<company_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_company(company_id):
    """Delete a company - admin only."""
    try:
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Delete the company - this will cascade delete related records
        response = supabase.table("os_construction").delete().eq("id", company_id).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to delete company")
            
        return jsonify({"message": f"Company with ID {company_id} deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to delete company: {str(e)}")

# Service endpoints
@app.route("/api/companies/<company_id>/services", methods=["GET"])
def get_company_services(company_id):
    """Get all services for a company with pagination."""
    try:
        # Get pagination parameters
        page, per_page = get_pagination_params()
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Get total count
        total_count = get_total_count(supabase, "os_construction_services")
        
        # Execute query with pagination
        query = supabase.table("os_construction_services").select("*").eq("company_id", company_id)
        query = paginate_query(query, page, per_page)
        response = query.execute()
        
        # Format and return response
        result = format_paginated_response(response.data, page, per_page, total_count)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error fetching services for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to retrieve services: {str(e)}")

@app.route("/api/companies/<company_id>/services", methods=["POST"])
@token_required
def add_company_service(company_id):
    """Add a new service for a company."""
    try:
        # Parse and validate input data
        data = request.json
        if not data:
            raise ValidationError("No data provided")
        
        # Validate with Pydantic model
        service_data = ServiceCreate(**data)
        
        # Check if company exists
        supabase = get_supabase_client()
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Prepare data for database
        db_data = service_data.dict()
        db_data["company_id"] = company_id
        
        # Add timestamps
        now = datetime.datetime.utcnow().isoformat()
        db_data["created_at"] = now
        db_data["updated_at"] = now
        
        # Insert into database
        response = supabase.table("os_construction_services").insert(db_data).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to create service")
            
        return jsonify(response.data[0]), 201
        
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise ValidationError(f"Invalid data: {'; '.join(error_messages)}")
        
    except Exception as e:
        app.logger.error(f"Error adding service for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to add service: {str(e)}")

# Project endpoints
@app.route("/api/companies/<company_id>/projects", methods=["GET"])
def get_company_projects(company_id):
    """Get all projects for a company with pagination and filtering."""
    try:
        # Get pagination parameters
        page, per_page = get_pagination_params()
        
        # Get filter parameters
        status = request.args.get("status")
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Build query
        query = supabase.table("os_construction_projects").select("*").eq("company_id", company_id)
        
        if status:
            valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'on_hold']
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status. Must be one of {valid_statuses}")
            query = query.eq("status", status)
        
        # Get total count (filtered)
        total_response = query.execute()
        total_count = len(total_response.data)
        
        # Apply pagination
        query = paginate_query(query, page, per_page)
        response = query.execute()
        
        # Format and return response
        result = format_paginated_response(response.data, page, per_page, total_count)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error fetching projects for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to retrieve projects: {str(e)}")

@app.route("/api/companies/<company_id>/projects", methods=["POST"])
@token_required
def add_company_project(company_id):
    """Add a new project for a company."""
    try:
        # Parse and validate input data
        data = request.json
        if not data:
            raise ValidationError("No data provided")
        
        # Validate with Pydantic model
        project_data = ProjectCreate(**data)
        
        # Check if company exists
        supabase = get_supabase_client()
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Prepare data for database
        db_data = project_data.dict()
        db_data["company_id"] = company_id
        
        # Handle date fields - convert to ISO format strings if present
        if db_data.get("start_date"):
            db_data["start_date"] = db_data["start_date"].isoformat()
        if db_data.get("end_date"):
            db_data["end_date"] = db_data["end_date"].isoformat()
        
        # Add timestamps
        now = datetime.datetime.utcnow().isoformat()
        db_data["created_at"] = now
        db_data["updated_at"] = now
        
        # Insert into database
        response = supabase.table("os_construction_projects").insert(db_data).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to create project")
            
        return jsonify(response.data[0]), 201
        
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise ValidationError(f"Invalid data: {'; '.join(error_messages)}")
        
    except Exception as e:
        app.logger.error(f"Error adding project for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to add project: {str(e)}")

# Employee endpoints
@app.route("/api/companies/<company_id>/employees", methods=["GET"])
def get_company_employees(company_id):
    """Get all employees for a company with pagination."""
    try:
        # Get pagination parameters
        page, per_page = get_pagination_params()
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Get total count
        query = supabase.table("os_construction_employees").select("count", count="exact").eq("company_id", company_id)
        count_response = query.execute()
        total_count = count_response.count if hasattr(count_response, 'count') else 0
        
        # Execute query with pagination
        query = supabase.table("os_construction_employees").select("*").eq("company_id", company_id)
        query = paginate_query(query, page, per_page)
        response = query.execute()
        
        # Format and return response
        result = format_paginated_response(response.data, page, per_page, total_count)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error fetching employees for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to retrieve employees: {str(e)}")

@app.route("/api/companies/<company_id>/employees", methods=["POST"])
@token_required
def add_company_employee(company_id):
    """Add a new employee for a company."""
    try:
        # Parse and validate input data
        data = request.json
        if not data:
            raise ValidationError("No data provided")
        
        # Validate with Pydantic model
        employee_data = EmployeeCreate(**data)
        
        # Check if company exists
        supabase = get_supabase_client()
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise ResourceNotFoundError(f"Company with ID {company_id} not found")
        
        # Prepare data for database
        db_data = employee_data.dict()
        db_data["company_id"] = company_id
        
        # Handle date field - convert to ISO format string if present
        if db_data.get("join_date"):
            db_data["join_date"] = db_data["join_date"].isoformat()
        
        # Add timestamps
        now = datetime.datetime.utcnow().isoformat()
        db_data["created_at"] = now
        db_data["updated_at"] = now
        
        # Insert into database
        response = supabase.table("os_construction_employees").insert(db_data).execute()
        
        if not response.data:
            raise DatabaseConnectionError("Failed to create employee")
            
        return jsonify(response.data[0]), 201
        
    except PydanticValidationError as e:
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        raise ValidationError(f"Invalid data: {'; '.join(error_messages)}")
        
    except Exception as e:
        app.logger.error(f"Error adding employee for company {company_id}: {e}")
        if isinstance(e, OSConstructionError):
            raise
        raise DatabaseConnectionError(f"Failed to add employee: {str(e)}")

if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG', False))