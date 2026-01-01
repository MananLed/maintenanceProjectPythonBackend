from dataclasses import is_dataclass, asdict
from pydantic import BaseModel 
from typing import Any 

def serialize(data: Any):
    if data is None:
        return None 
    
    if isinstance(data, (list, tuple)):
        return [serialize(item) for item in data]
    
    if is_dataclass(data):
        return asdict(data)
    
    if isinstance(data, BaseModel):
        return data.model_dump()
    
    if isinstance(data, dict):
        return {k: serialize(v) for k, v in data.items()}
    
    return data