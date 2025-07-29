# endpoint registry logic
from threading import Lock
from typing import Dict


# Thread-safe in-memory registry
class EndpointRegistry:
    def __init__(self):
        self._registry: Dict[str, Dict] = {}
        self._lock = Lock()

    def add(self, endpoint_name: str, config: Dict):
        with self._lock:
            self._registry[endpoint_name] = config

    def update(self, endpoint_name: str, config: Dict):
        with self._lock:
            if endpoint_name in self._registry:
                self._registry[endpoint_name].update(config)

    def delete(self, endpoint_name: str):
        with self._lock:
            self._registry.pop(endpoint_name, None)

    def get(self, endpoint_name: str) -> Dict:
        return self._registry.get(endpoint_name, {})

    def list_all(self) -> Dict[str, Dict]:
        return self._registry.copy()
