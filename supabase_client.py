import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Initialize and return a cached Supabase client.
    
    Uses lru_cache for connection pooling to improve performance.
    
    Returns:
        Client: A Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are missing
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    return create_client(supabase_url, supabase_key)