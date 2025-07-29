"""JSON utilities for the Dravik project"""
import json
from datasets import Version

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle special types"""
    def default(self, obj):
        if isinstance(obj, Version):
            return str(obj)  # Convert Version object to string
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()  # Convert objects with to_dict method
        elif hasattr(obj, '__dict__'):
            return obj.__dict__  # Convert objects with __dict__ attribute
        try:
            # Try to convert to string as last resort
            return str(obj)
        except:
            return f"<Unserializable object of type {type(obj).__name__}>"
