from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from osconstruction import create_client
from werkzeug.exceptions import BadRequest, NotFound

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
def get_supabase_client():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    return create_client(supabase_url, supabase_key)

# Error handling
@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "Bad Request", "message": str(e)}), 400

@app.errorhandler(NotFound)
def handle_not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404

@app.errorhandler(Exception)
def handle_generic_exception(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# Company endpoints
@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Get all construction companies"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("os_construction").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        app.logger.error(f"Error fetching companies: {e}")
        raise

@app.route("/api/companies/<company_id>", methods=["GET"])
def get_company(company_id):
    """Get a specific company by ID"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("os_construction").select("*").eq("id", company_id).execute()
        
        if not response.data:
            raise NotFound(f"Company with ID {company_id} not found")
            
        return jsonify(response.data[0])
    except Exception as e:
        app.logger.error(f"Error fetching company {company_id}: {e}")
        raise

@app.route("/api/companies", methods=["POST"])
def create_company():
    """Create a new company"""
    try:
        data = request.json
        
        if not data:
            raise BadRequest("No data provided")
            
        required_fields = ["company_name", "company_address", "company_email", "company_phone"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        supabase = get_supabase_client()
        response = supabase.table("os_construction").insert(data).execute()
        
        return jsonify(response.data[0]), 201
    except Exception as e:
        app.logger.error(f"Error creating company: {e}")
        raise

@app.route("/api/companies/<company_id>", methods=["PUT"])
def update_company(company_id):
    """Update an existing company"""
    try:
        data = request.json
        
        if not data:
            raise BadRequest("No data provided")
            
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        response = supabase.table("os_construction").update(data).eq("id", company_id).execute()
        
        return jsonify(response.data[0])
    except Exception as e:
        app.logger.error(f"Error updating company {company_id}: {e}")
        raise

@app.route("/api/companies/<company_id>", methods=["DELETE"])
def delete_company(company_id):
    """Delete a company"""
    try:
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        supabase.table("os_construction").delete().eq("id", company_id).execute()
        
        return jsonify({"message": f"Company with ID {company_id} deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting company {company_id}: {e}")
        raise

# Service endpoints
@app.route("/api/companies/<company_id>/services", methods=["GET"])
def get_company_services(company_id):
    """Get all services for a company"""
    try:
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        response = supabase.table("os_construction_services").select("*").eq("company_id", company_id).execute()
        
        return jsonify(response.data)
    except Exception as e:
        app.logger.error(f"Error fetching services for company {company_id}: {e}")
        raise

@app.route("/api/companies/<company_id>/services", methods=["POST"])
def add_company_service(company_id):
    """Add a new service for a company"""
    try:
        data = request.json
        
        if not data:
            raise BadRequest("No data provided")
            
        required_fields = ["service_name"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        # Add company_id to data
        data["company_id"] = company_id
        
        response = supabase.table("os_construction_services").insert(data).execute()
        
        return jsonify(response.data[0]), 201
    except Exception as e:
        app.logger.error(f"Error adding service for company {company_id}: {e}")
        raise

# Project endpoints
@app.route("/api/companies/<company_id>/projects", methods=["GET"])
def get_company_projects(company_id):
    """Get all projects for a company"""
    try:
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        # Get optional status filter
        status = request.args.get("status")
        
        query = supabase.table("os_construction_projects").select("*").eq("company_id", company_id)
        
        if status:
            query = query.eq("status", status)
            
        response = query.execute()
        
        return jsonify(response.data)
    except Exception as e:
        app.logger.error(f"Error fetching projects for company {company_id}: {e}")
        raise

@app.route("/api/companies/<company_id>/projects", methods=["POST"])
def add_company_project(company_id):
    """Add a new project for a company"""
    try:
        data = request.json
        
        if not data:
            raise BadRequest("No data provided")
            
        required_fields = ["project_name", "location"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        # Add company_id to data
        data["company_id"] = company_id
        
        response = supabase.table("os_construction_projects").insert(data).execute()
        
        return jsonify(response.data[0]), 201
    except Exception as e:
        app.logger.error(f"Error adding project for company {company_id}: {e}")
        raise

# Employee endpoints
@app.route("/api/companies/<company_id>/employees", methods=["GET"])
def get_company_employees(company_id):
    """Get all employees for a company"""
    try:
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        response = supabase.table("os_construction_employees").select("*").eq("company_id", company_id).execute()
        
        return jsonify(response.data)
    except Exception as e:
        app.logger.error(f"Error fetching employees for company {company_id}: {e}")
        raise

@app.route("/api/companies/<company_id>/employees", methods=["POST"])
def add_company_employee(company_id):
    """Add a new employee for a company"""
    try:
        data = request.json
        
        if not data:
            raise BadRequest("No data provided")
            
        required_fields = ["full_name", "position"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        supabase = get_supabase_client()
        
        # First, check if company exists
        check = supabase.table("os_construction").select("id").eq("id", company_id).execute()
        if not check.data:
            raise NotFound(f"Company with ID {company_id} not found")
        
        # Add company_id to data
        data["company_id"] = company_id
        
        response = supabase.table("os_construction_employees").insert(data).execute()
        
        return jsonify(response.data[0]), 201
    except Exception as e:
        app.logger.error(f"Error adding employee for company {company_id}: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True)