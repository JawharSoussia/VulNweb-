"""Model Versioning and Registry"""
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelVersionManager:
    """Manage model versions"""

    def __init__(self, registry_file: str = "ml_model/inference/model_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        """Load version registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {'versions': []}

    def register_model(self, model_name: str, model_version: str, metadata: dict):
        """Register new model version"""
        entry = {
            'model_name': model_name,
            'version': model_version,
            'timestamp': datetime.now().isoformat(),
            'metrics': metadata.get('cv_results', {}),
            'status': 'active'
        }

        self.registry['versions'].append(entry)
        self._save_registry()
        logger.info(f"✓ Registered: {model_name} v{model_version}")

    def _save_registry(self):
        """Save registry to disk"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def get_latest_version(self) -> dict:
        """Get latest model version"""
        if self.registry['versions']:
            return self.registry['versions'][-1]
        return None

    def list_versions(self):
        """List all registered versions"""
        for entry in self.registry['versions']:
            logger.info(f"  {entry['model_name']} v{entry['version']} ({entry['timestamp']})")