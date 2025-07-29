from fastapi import APIRouter, Request
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
        except ValueError as e:
            logger.error(f"Path error: {e}")
            raise

        parts = []
        for part in relative_path.parts:
            if part == 'index':
                continue
            if part.startswith('_'):
                continue
            # Ne traite que les fichiers {param}.py comme paramètres
            if (part.startswith('{') and part.endswith('}') and 
                filepath.parent.name == part[1:-1]):
                part = f"{{{part[1:-1]}}}"
            parts.append(part)
        
        return '/' + '/'.join(parts)

    @staticmethod
    def _get_route_params(module: Any) -> Dict[str, Any]:
        """Extrait les paramètres de la fonction handler"""
        handler = None
        if hasattr(module, 'get'):
            handler = module.get
        elif hasattr(module, 'default'):
            handler = module.default
        
        if not handler:
            return {}
        
        sig = inspect.signature(handler)
        return {
            name: param.default if param.default != inspect.Parameter.empty else ...
            for name, param in sig.parameters.items()
            if name not in ['request', 'self']
        }

    @classmethod
    def register_routes(cls, router: APIRouter, base_path: Union[Path, str]):
        """Enregistre toutes les routes"""
        if isinstance(base_path, str):
            base_path = Path(base_path)
        base_path = base_path.resolve()

        # Ajout temporaire au PYTHONPATH
        parent_dir = str(base_path.parent)
        original_sys_path = sys.path.copy()
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            for filepath in base_path.glob('**/*.py'):
                if filepath.name.startswith(('_', '.')):
                    continue

                # Ignorer les fichiers avec {param} s'ils ne sont pas dans un répertoire du même nom
                if filepath.stem.startswith('{') and filepath.stem.endswith('}'):
                    parent_dir_name = filepath.parent.name
                    if parent_dir_name != filepath.stem[1:-1]:
                        continue

                try:
                    route_path = cls._get_route_path(filepath, base_path)
                    module_path = '.'.join(filepath.relative_to(base_path.parent).with_suffix('').parts)

                    module = importlib.import_module(module_path)
                    
                    # Enregistrement des méthodes HTTP
                    for method in ['get', 'post', 'put', 'delete', 'patch']:
                        if hasattr(module, method):
                            handler = getattr(module, method)
                            getattr(router, method)(
                                route_path,
                                **({'response_model': handler.__annotations__.get('return')} 
                                if hasattr(handler, '__annotations__') else {})
                            )(handler)
                    
                    # Fallback pour default
                    if hasattr(module, 'default') and not any(hasattr(module, m) for m in ['get', 'post', 'put', 'delete', 'patch']):
                        handler = module.default
                        router.get(route_path)(handler)

                    logger.info(f"Route registered: {route_path} -> {module_path}")

                except ImportError as e:
                    logger.error(f"Import error for {filepath}: {e}")
                except Exception as e:
                    logger.error(f"Error loading route {filepath}: {e}")

        finally:
            sys.path = original_sys_path