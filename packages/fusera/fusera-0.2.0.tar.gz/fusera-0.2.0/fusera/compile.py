import torch
import requests
import tempfile
import time
import os
import uuid
from pathlib import Path
from .exceptions import APIKeyError, UploadError, FileTooLargeError

API_URL = os.environ.get("FUSERA_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("FUSERA_API_KEY", "")
DEV_MODE = os.environ.get("FUSERA_DEV_MODE", "").lower() in ("true", "1", "yes")

# Local storage for dev mode
DEV_JOBS = {}
DEV_CACHE_DIR = Path.home() / ".fusera_dev"

def compile(model):
    """
    Submit model for compilation. Returns job details with dashboard URL.
    
    Args:
        model: PyTorch model to compile
        
    Returns:
        dict: {
            'job_id': str,
            'dashboard_url': str, 
            'message': str
        }
    """
    if DEV_MODE:
        return _dev_compile(model)
    
    # Validate API key
    if not API_KEY:
        raise APIKeyError(
            "FUSERA_API_KEY environment variable not set. "
            "Get your API key at https://fusera.dev/dashboard"
        )
    
    if not API_KEY.startswith('fus_'):
        raise APIKeyError(
            "Invalid API key format. "
            "Get a valid API key at https://fusera.dev/dashboard"
        )
    
    with tempfile.NamedTemporaryFile(suffix='.pth') as tmp:
        torch.jit.save(torch.jit.script(model), tmp.name)
        
        with open(tmp.name, 'rb') as f:
            response = requests.post(
                f"{API_URL}/compile",
                files={'file': f},
                params={'api_key': API_KEY}  # FIXED: Use query params
            )
    
    if response.status_code == 401:
        raise APIKeyError(
            "Invalid API key. Please check:\n"
            "1. Your FUSERA_API_KEY environment variable is set correctly\n"
            "2. The API key starts with 'fus_'\n"
            "3. The key hasn't been deactivated\n"
            "Get a new key at: https://fusera.dev/dashboard"
        )
    elif response.status_code == 413:
        raise FileTooLargeError("Model file too large. Maximum size is 1GB.")
    elif response.status_code != 200:
        raise UploadError(f"Upload failed: {response.text}")
    
    job_id = response.json()['job_id']
    dashboard_url = f"https://fusera.dev/jobs/{job_id}"
    
    return {
        'job_id': job_id,
        'dashboard_url': dashboard_url,
        'message': f"✓ Model submitted! Track progress at: {dashboard_url}"
    }


def _dev_compile(model):
    """Dev mode: compile locally with torch.compile"""
    job_id = str(uuid.uuid4())
    
    print("🔧 [DEV MODE] Compiling locally with torch.compile...")
    
    try:
        # Compile with torch.compile
        compiled = torch.compile(model, backend="aot_eager")
        
        # Test compilation
        dummy_input = torch.randn(1, 10)
        _ = compiled(dummy_input)
        
        # Create cache directory
        DEV_CACHE_DIR.mkdir(exist_ok=True)
        
        # Save model
        model_path = DEV_CACHE_DIR / f"{job_id}.pth"
        torch.jit.save(torch.jit.script(model), model_path)
        
        # Save job info
        DEV_JOBS[job_id] = {
            'status': 'completed',  # Immediate completion in dev mode
            'created_at': time.time(),
            'model_path': str(model_path)
        }
        
        dashboard_url = f"http://localhost:3000/jobs/{job_id}"
        
        return {
            'job_id': job_id,
            'dashboard_url': dashboard_url,
            'message': f"✓ [DEV MODE] Model compiled! View at: {dashboard_url}"
        }
        
    except Exception as e:
        print(f"❌ [DEV MODE] Local compilation failed: {e}")
        job_id = str(uuid.uuid4())
        dashboard_url = f"http://localhost:3000/jobs/{job_id}"
        
        return {
            'job_id': job_id,
            'dashboard_url': dashboard_url,
            'message': f"❌ [DEV MODE] Compilation failed. View details at: {dashboard_url}"
        }

