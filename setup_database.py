import os
from supabase import create_client, Client

# Initialize Supabase client
def initialize_supabase():
    # Replace with your actual Supabase URL and API key
    # It's recommended to use environment variables for security
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    return supabase

# Create the OSConstruction table
def create_os_construction_table(supabase):
    # SQL for creating the table
    # Note: This is using the PostgreSQL SQL syntax which Supabase supports
    sql = """
    CREATE TABLE IF NOT EXISTS os_construction (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        company_name VARCHAR(255) NOT NULL,
        company_address TEXT NOT NULL,
        company_email VARCHAR(255) NOT NULL,
        company_phone VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Execute the SQL query
    response = supabase.table("os_construction").execute(sql)
    return response

# Insert a sample row into the OSConstruction table
def insert_sample_data(supabase):
    data = {
        "company_name": "OSConstruction Services",
        "company_address": "123 Builder Avenue, Construction City, CC 12345",
        "company_email": "info@osconstruction.example.com",
        "company_phone": "+1-555-123-4567"
    }
    
    response = supabase.table("os_construction").insert(data).execute()
    return response

# Retrieve all rows from the OSConstruction table
def get_all_os_construction(supabase):
    response = supabase.table("os_construction").select("*").execute()
    return response

# Usage example
if __name__ == "__main__":
    try:
        # Set these environment variables before running
        # export SUPABASE_URL=your_supabase_url
        # export SUPABASE_KEY=your_supabase_key
        
        # Initialize the client
        supabase = initialize_supabase()
        
        # Create the table
        create_os_construction_table(supabase)
        print("Table created successfully!")
        
        # Insert sample data
        insert_result = insert_sample_data(supabase)
        print(f"Sample data inserted: {insert_result}")
        
        # Retrieve all data
        all_data = get_all_os_construction(supabase)
        print("All OSConstruction records:")
        for record in all_data.data:
            print(record)
            
    except Exception as e:
        print(f"Error: {e}")