from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
import sys
from pathlib import Path
import os

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from auth import get_current_user, User
from packages.db.session import get_session
from packages.db.crud import get_all_prompt_versions
from storage.file_storage import FileStorage

router = APIRouter(prefix="/api/storage", tags=["storage"])

# Initialize limiter (will use app.state.limiter from main)
limiter = Limiter(key_func=get_remote_address)

# Endpoints

@router.post("/export-multi-agent")
@limiter.limit("10/minute")
async def export_multi_agent_csv(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export multi-agent results from database to CSV.
    
    Database-First Pattern:
    - Reads from PostgreSQL (single source of truth)
    - Generates CSV for analysis/backup
    - Manual export (not automatic)
    """
    try:
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        storage = FileStorage(base_dir=storage_dir, db_session=session)
        
        csv_path = storage.export_multi_agent_results_to_csv()
        
        # Count records
        versions = get_all_prompt_versions(session, limit=1000)
        by_prompt = {}
        for v in versions:
            if v.prompt_id not in by_prompt:
                by_prompt[v.prompt_id] = []
        
        return {
            "success": True,
            "csv_path": csv_path,
            "records": len(by_prompt)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/export-temporal")
@limiter.limit("10/minute")
async def export_temporal_csv(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export temporal version chains from database to CSV.
    
    Database-First Pattern:
    - Reads from PostgreSQL (single source of truth)
    - Generates CSV for analysis/backup
    - Manual export (not automatic)
    """
    try:
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        storage = FileStorage(base_dir=storage_dir, db_session=session)
        
        csv_path = storage.export_temporal_versions_to_csv()
        
        # Count records
        versions = get_all_prompt_versions(session, limit=1000)
        
        return {
            "success": True,
            "csv_path": csv_path,
            "records": len(versions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/export-all")
@limiter.limit("5/minute")
async def export_all_csv(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export all data from database to CSV files.
    
    Database-First Pattern:
    - Exports multi-agent + temporal data
    - Single endpoint for bulk export
    """
    try:
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        storage = FileStorage(base_dir=storage_dir, db_session=session)
        
        paths = storage.export_all_to_csv()
        
        return {
            "success": True,
            "csv_paths": paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
