from typing import Any, Union
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

def init_app(app_root: Union[Path, str] = None):
    """Initialise toutes les ressources"""
    if app_root is None:
        app_root = Path(__file__).parent.parent
    if isinstance(app_root, str):
        app_root = Path(app_root)
    
    _intl.set_project_root(app_root.resolve())
    _config.set_project_root(app_root.resolve())
    _intl.load_all()
    _config.load_all()

def t(key: str, locale: str = 'fr', module: str = "global", **kwargs) -> str:
    """Récupère une traduction"""
    value = _intl.get(module, key, locale) or key
    return value.format(**kwargs) if kwargs else value

def cfg(key: str, default: Any = None, module: str = "global") -> Any:
    """Récupère une configuration"""
    return _config.get(module, key, default)

def register_routes(router: APIRouter, base_path: Union[Path, str]):
    """Enregistre les routes"""
    if isinstance(base_path, str):
        base_path = Path(base_path)
    _router.register_routes(router, base_path.resolve())