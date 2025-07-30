"""PyConfBox - Python configuration management with multiple storage backends."""

__version__ = "0.1.0"

from .core.config import Config
from .core.exceptions import (
    PyConfBoxError,
    ConfigNotFoundError,
    ImmutableConfigError,
    ConfigTypeError,
    StorageError,
    PluginError,
    ReleasedConfigError,
    ScopeError,
)
from .core.types import ConfigScope, ConfigValue, ConfigMetadata
from .storage.base import BaseStorage, ReadOnlyStorage
from .storage.memory import MemoryStorage
from .storage.environment import EnvironmentStorage, WritableEnvironmentStorage
from .storage.file import FileStorage, JSONStorage, YAMLStorage, TOMLStorage
from .storage.redis import RedisStorage
from .storage.sqlite import SQLiteStorage

__all__ = [
    # 버전
    "__version__",
    
    # 메인 클래스
    "Config",
    
    # 예외
    "PyConfBoxError",
    "ConfigNotFoundError", 
    "ImmutableConfigError",
    "ConfigTypeError",
    "StorageError",
    "PluginError",
    "ReleasedConfigError",
    "ScopeError",
    
    # 타입
    "ConfigScope",
    "ConfigValue", 
    "ConfigMetadata",
    
    # 저장소
    "BaseStorage",
    "ReadOnlyStorage",
    "MemoryStorage",
    "EnvironmentStorage",
    "WritableEnvironmentStorage",
    "FileStorage",
    "JSONStorage",
    "YAMLStorage", 
    "TOMLStorage",
    "RedisStorage",
    "SQLiteStorage",
]


