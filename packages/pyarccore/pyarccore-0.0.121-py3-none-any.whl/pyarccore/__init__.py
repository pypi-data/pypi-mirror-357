from typing import Any
from fastapi import FastAPI, APIRouter
from pathlib import Path
from .internationalisation_manager import InternationalisationManager
from .config_manager import ConfigManager
from .router import ArcCmsRouter
import logging

logger = logging.getLogger(__name__)

_intl = InternationalisationManager()
_config = ConfigManager()
_router = ArcCmsRouter()

def init_app(app_root: Path = None):
    """Initialise toutes les ressources"""
    if app_root is None:
        # Par défaut, on prend le répertoire parent du package
        app_root = Path(__file__).parent.parent.resolve()
    
    _intl.set_project_root(app_root)
    _config.set_project_root(app_root)
    _intl.load_all()
    _config.load_all()

def t(key: str, locale: str = 'fr', module: str = "global", **kwargs) -> str:
    """Récupère une traduction"""
    value = _intl.get(module, key, locale) or key
    return value.format(**kwargs) if kwargs else value

def cfg(key: str, default: Any = None, module: str = "global") -> Any:
    """Récupère une configuration"""
    return _config.get(module, key, default)

def register_routes(router: APIRouter, base_path: str | Path):
    """Enregistre les routes"""
    path_obj = Path(base_path).resolve() if isinstance(base_path, str) else base_path.resolve()
    _router.register_routes(router, path_obj)