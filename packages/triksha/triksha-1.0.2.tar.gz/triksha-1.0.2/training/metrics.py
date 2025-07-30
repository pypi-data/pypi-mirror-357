"""Metrics tracking and management for training"""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any

class TrainingMetrics:
    """Handle training metrics storage and retrieval"""
    
    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
        
    def save_training_metrics(self, run_id: str, metrics: Dict[str, Any]) -> bool:
        """Save metrics for a training run"""
        try:
            epoch = metrics.get("epoch", 0)
            loss = metrics.get("loss", 0.0)
            learning_rate = metrics.get("learning_rate", 0.0)
            timestamp = metrics.get("timestamp", datetime.now().timestamp())
            
            # Extract other metrics
            other_metrics = {k: v for k, v in metrics.items() 
                           if k not in ["epoch", "loss", "learning_rate", "timestamp"]}
            
            cursor = self.db.cursor()
            cursor.execute('''
            INSERT INTO training_metrics
            (run_id, epoch, loss, learning_rate, timestamp, metrics)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                epoch,
                loss,
                learning_rate,
                timestamp,
                json.dumps(other_metrics)
            ))
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error saving metrics: {str(e)}")
            return False
