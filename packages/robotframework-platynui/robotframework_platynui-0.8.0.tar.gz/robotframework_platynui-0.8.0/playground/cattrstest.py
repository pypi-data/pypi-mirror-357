from dataclasses import dataclass
from typing import Any, Union, get_args, get_origin

from cattrs.preconf.json import make_converter

# 0) Converter anlegen
converter = make_converter()

# 1) Factory für list[...] registrieren
converter.register_structure_hook_factory(
    lambda t: get_origin(t) is list,
    lambda t: (lambda obj, _: list(obj))
)

# 2) Factory für dict[...] registrieren
converter.register_structure_hook_factory(
    lambda t: get_origin(t) is dict,
    lambda t: (lambda obj, _: dict(obj))
)

# 3) Factory für Union[list[...], dict[...], None] (z.B. params)
def is_list_dict_union(t):
    if get_origin(t) is not Union:
        return False
    args = get_args(t)
    # Nicht-None-Typen (für Optional)
    non_none = [a for a in args if a is not type(None)]
    # alle Nicht-None müssen list oder dict sein
    return bool(non_none) and all(get_origin(a) in (list, dict) for a in non_none)


def list_dict_union_factory(t):
    args = get_args(t)
    containers = [a for a in args if get_origin(a) in (list, dict)]
    def struct_union(obj, _):
        # None einfach durchreichen
        if obj is None:
            return None
        # je nach Instanztyp in den passenden Container strukturieren
        for cont in containers:
            origin = get_origin(cont)
            if origin is list and isinstance(obj, list):
                return converter.structure(obj, cont)
            if origin is dict and isinstance(obj, dict):
                return converter.structure(obj, cont)
        raise TypeError(f"Cannot build {t} from {type(obj)}")
    return struct_union

converter.register_structure_hook_factory(
    is_list_dict_union,
    list_dict_union_factory
)

# 4) JSON-RPC Dataclasses
@dataclass
class JsonRpcRequest:
    jsonrpc: str
    method: str
    params: list[Any] | dict[str, Any] | None
    id: int

@dataclass
class JsonRpcNotification:
    jsonrpc: str
    method: str
    params: list[Any] | dict[str, Any] | None

@dataclass
class JsonRpcResponse:
    jsonrpc: str
    result: Any
    id: int

@dataclass
class JsonRpcErrorResponse:
    jsonrpc: str
    error: Any
    id: int

# 5) Union-Typ für alle Nachrichten
JsonRpcMessage = Union[
    JsonRpcRequest,
    JsonRpcNotification,
    JsonRpcResponse,
    JsonRpcErrorResponse,
]

# 6) Dispatch-Funktion für die Union

def struct_rpc_message(obj: dict, _: type[JsonRpcMessage]) -> JsonRpcMessage:
    if not isinstance(obj, dict):
        raise TypeError(f"Kann JSON-RPC-Message nur aus dict bauen, nicht aus {type(obj)}")
    version = obj.get("jsonrpc")
    if version != "2.0":
        raise ValueError(f"Unsupported JSON-RPC version: {version!r}")

    if "method" in obj:
        # Requests haben immer 'id', Notifications nicht
        target = JsonRpcRequest if "id" in obj else JsonRpcNotification
    else:
        # Responses ohne 'method'
        target = JsonRpcErrorResponse if "error" in obj else JsonRpcResponse

    # Strukturieren mit dem gewählten Zieltypen
    return converter.structure(obj, target)

# 7) Hook registrieren
converter.register_structure_hook(JsonRpcMessage, struct_rpc_message)

# 8) Test-Beispiele
def main():
    examples = [
        '{"jsonrpc":"2.0","method":"foo","params":[1,2,3],"id":42}',
        '{"jsonrpc":"2.0","method":"bar","params":{"a":10,"b":20}}',
        '{"jsonrpc":"2.0","result":true,"id":42}',
        '{"jsonrpc":"2.0","error":{"code":-32601,"message":"Not found"},"id":42}',
    ]
    for js in examples:
        msg = converter.loads(js, JsonRpcMessage)
        print(type(msg).__name__, msg)

if __name__ == "__main__":
    main()
