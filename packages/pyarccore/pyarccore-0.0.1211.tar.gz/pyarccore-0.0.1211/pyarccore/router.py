from fastapi import APIRouter
from pathlib import Path
import importlib
import inspect
import sys
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class ArcCmsRouter:
    @staticmethod
    def _get_route_path(filepath: Path, base_path: Path) -> str:
        """Convertit le chemin du fichier en route"""
        try:
            relative_path = filepath.resolve().relative_to(base_path.resolve()).with_suffix('')
        except ValueError:
            logger.error(f"File {filepath} is not in base path {base_path}")
            raise

        parts = []
        for part in relative_path.parts:
            if part == 'index':
                continue
            if part.startswith('_'):
                continue
            if part.startswith('[') and part.endswith(']'):
                part = f"{{{part[1:-1]}}}"
            parts.append(part)
        
        return '/' + '/'.join(parts)

    @staticmethod
    def _get_route_params(module: Any) -> Dict[str, Any]:
        """Extrait les paramètres de la fonction handler"""
        if hasattr(module, 'get'):
            func = module.get
        elif hasattr(module, 'default'):
            func = module.default
        else:
            return {}
        
        sig = inspect.signature(func)
        return {
            name: param.default if param.default != inspect.Parameter.empty else ...
            for name, param in sig.parameters.items()
            if name not in ['request', 'self']
        }

    @classmethod
    def register_routes(cls, router: APIRouter, base_path: Union[Path, str]):
        """Enregistre toutes les routes avec gestion des paramètres"""
        if isinstance(base_path, str):
            base_path = Path(base_path)
        base_path = base_path.resolve()
        
        # Ajout temporaire du répertoire parent au PYTHONPATH
        parent_dir = str(base_path.parent)
        original_sys_path = sys.path.copy