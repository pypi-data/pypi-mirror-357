from fastapi import APIRouter
from pathlib import Path
import importlib
import inspect
import sys
from typing import Dict, Any
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
    def register_routes(cls, router: APIRouter, base_path: Path | str):
        """Enregistre toutes les routes avec gestion des paramètres"""
        base_path = Path(base_path).resolve() if isinstance(base_path, str) else base_path.resolve()
        
        # Ajout temporaire du répertoire parent au PYTHONPATH
        parent_dir = str(base_path.parent)
        original_sys_path = sys.path.copy()
        
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            for filepath in base_path.glob('**/*.py'):
                filepath = filepath.resolve()
                if filepath.name.startswith(('_', '.')) or not filepath.is_file():
                    continue

                try:
                    route_path = cls._get_route_path(filepath, base_path)
                    module_path = '.'.join(filepath.relative_to(base_path.parent).with_suffix('').parts)
                    
                    try:
                        module = importlib.import_module(module_path)
                        params = cls._get_route_params(module)
                        
                        # Enregistrement des méthodes HTTP
                        for method in ['get', 'post', 'put', 'delete', 'patch']:
                            if hasattr(module, method):
                                handler = getattr(module, method)
                                getattr(router, method)(
                                    route_path,
                                    **({'response_model': handler.__annotations__.get('return')} 
                                       if hasattr(handler, '__annotations__') else {})
                                )(handler)
                        
                        # Fallback pour export default
                        if (hasattr(module, 'default') and 
                            not any(hasattr(module, m) for m in ['get', 'post', 'put', 'delete', 'patch'])):
                            handler = module.default
                            router.get(
                                route_path,
                                **({'response_model': handler.__annotations__.get('return')} 
                                   if hasattr(handler, '__annotations__') else {})
                            )(handler)
                        
                        logger.info(f"Route registered: {route_path} -> {module_path}")
                        
                    except ImportError as e:
                        logger.error(f"Import error for {filepath}: {e}")
                    except Exception as e:
                        logger.error(f"Error loading route {filepath}: {e}")

                except ValueError as e:
                    logger.error(f"Path error for {filepath}: {e}")
                    continue

        finally:
            # Restaure le PYTHONPATH original
            sys.path = original_sys_path