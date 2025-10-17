"""
Google Earth Engine Authentication Module

Supports both local file-based authentication and Streamlit Cloud secrets
"""

import ee
import json
from pathlib import Path

def initialize_gee():
    """
    Initialize Google Earth Engine with support for both local and Streamlit Cloud
    
    Priority:
    1. Try Streamlit secrets (for cloud deployment)
    2. Fall back to local service account file (for local development)
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'gee' in st.secrets:
            # Get credentials from Streamlit secrets
            credentials_dict = dict(st.secrets['gee'])
            credentials = ee.ServiceAccountCredentials(
                email=credentials_dict['client_email'],
                key_data=json.dumps(credentials_dict)
            )
            ee.Initialize(credentials)
            print("✅ GEE initialized with Streamlit secrets")
            return True
    except Exception as e:
        print(f"⚠️ Streamlit secrets not available: {e}")
    
    # Fall back to local service account file
    try:
        service_account_file = Path(__file__).parent / 'keys' / 'service_account.json'
        
        if not service_account_file.exists():
            print(f"❌ Service account file not found: {service_account_file}")
            return False
        
        # Read the service account credentials
        with open(service_account_file, 'r') as f:
            credentials_dict = json.load(f)
        
        credentials = ee.ServiceAccountCredentials(
            email=credentials_dict['client_email'],
            key_file=str(service_account_file)
        )
        ee.Initialize(credentials)
        print(f"✅ GEE initialized with local file: {service_account_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize GEE: {e}")
        return False

def get_gee_credentials():
    """
    Get GEE credentials from either Streamlit secrets or local file
    
    Returns:
        dict: Service account credentials dictionary
    """
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'gee' in st.secrets:
            return dict(st.secrets['gee'])
    except:
        pass
    
    # Fall back to local file
    try:
        service_account_file = Path(__file__).parent / 'keys' / 'service_account.json'
        if service_account_file.exists():
            with open(service_account_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Failed to get credentials: {e}")
    
    return None

def is_gee_available():
    """
    Check if GEE credentials are available
    
    Returns:
        bool: True if credentials available, False otherwise
    """
    try:
        creds = get_gee_credentials()
        return creds is not None
    except:
        return False

# Example usage
if __name__ == "__main__":
    print("Testing GEE authentication...")
    if initialize_gee():
        print("✅ GEE authentication successful!")
        print("🌍 You can now use Google Earth Engine")
    else:
        print("❌ GEE authentication failed!")
        print("Please check your credentials")
