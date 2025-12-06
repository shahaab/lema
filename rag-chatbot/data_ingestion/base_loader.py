from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLoader(ABC):
    """Base class for all data loaders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collection_name = config.get('collection_name', 'default')
    
    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """
        Load data from source and return list of documents.
        Each document should have: {'content': str, 'metadata': dict}
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if this loader is enabled in config"""
        return self.config.get('enabled', False)

