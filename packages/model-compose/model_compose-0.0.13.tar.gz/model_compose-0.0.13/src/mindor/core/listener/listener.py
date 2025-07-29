from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from mindor.dsl.schema.listener import ListenerConfig
from .engine import ListenerEngine, ListenerEngineMap

def create_listener(config: ListenerConfig, env: Dict[str, str], daemon: bool) -> ListenerEngine:
    try:
        return ListenerEngineMap[config.type](config, env, daemon)
    except KeyError:
        raise ValueError(f"Unsupported listener type: {config.type}")
