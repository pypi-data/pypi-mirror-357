import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

class BackupManager:
    """Manager for handling benchmark session backups and result saving"""
    
    def __init__(self, sessions_dir: Optional[str] = None, results_dir: Optional[str] = None):
        """
        Initialize backup manager with configurable paths
        
        Args:
            sessions_dir: Optional custom path for sessions
            results_dir: Optional custom path for results
        """
        # Use Path.home() for dynamic paths instead of hardcoded paths
        self.sessions_dir = Path(sessions_dir) if sessions_dir else Path.home() / "dravik" / "benchmark_sessions"
        self.results_dir = Path(results_dir) if results_dir else Path.home() / "dravik" / "benchmark_results"
        
        # Create directories if they don't exist
        self.sessions_dir.mkdir(exist_ok=True, parents=True)
        self.results_dir.mkdir(exist_ok=True, parents=True)
    
    def create_session(self) -> str:
        """
        Create a new benchmark session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session_path = self.sessions_dir / f"{session_id}.json"
        
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        
        with open(session_path, 'w') as f:
            json.dump(session_data, f)
            
        return session_id
    
    def save_session_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save session state for resuming
        
        Args:
            session_id: Session identifier
            state: Current state to save
            
        Returns:
            Success status
        """
        try:
            session_path = self.sessions_dir / f"{session_id}.json"
            
            # Update existing file
            if session_path.exists():
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {
                    "session_id": session_id,
                    "created_at": datetime.now().isoformat(),
                    "status": "created"
                }
                
            # Update with new state
            session_data.update(state)
            session_data["updated_at"] = datetime.now().isoformat()
            
            with open(session_path, 'w') as f:
                json.dump(session_data, f)
                
            return True
        except Exception as e:
            print(f"Error saving session state: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        try:
            session_path = self.sessions_dir / f"{session_id}.json"
            
            if not session_path.exists():
                return None
                
            with open(session_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions
        
        Returns:
            List of session data
        """
        try:
            sessions = []
            
            if not self.sessions_dir.exists():
                return []
            
            for file_path in self.sessions_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception as e:
                    print(f"Error loading session file {file_path}: {e}")
            
            # Sort by created_at time, newest first
            sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        try:
            session_path = self.sessions_dir / f"{session_id}.json"
            
            if not session_path.exists():
                return False
                
            os.unlink(session_path)
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def save_benchmark_result(self, result: Dict[str, Any], model_name: str) -> Optional[str]:
        """
        Save benchmark result to file
        
        Args:
            result: Benchmark result data
            model_name: Model name for filename
            
        Returns:
            Path to saved file or None if save failed
        """
        try:
            # Ensure results directory exists
            self.results_dir.mkdir(exist_ok=True, parents=True)
            
            # Format model name for filename
            safe_model_name = model_name.replace('/', '_').replace(' ', '_')
            
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"{safe_model_name}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            # Save result data to file
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2)
                
            return str(filepath)
        except Exception as e:
            print(f"Error saving benchmark result: {e}")
            return None
