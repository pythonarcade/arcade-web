from pathlib import Path
from typing import Dict, Union

RESOURCE_PATH = Path(__file__).parent.resolve()

resource_handles: Dict[str, Path] = {
    "resources": RESOURCE_PATH,
}


def resolve_resource_path(path: Union[str, Path]) -> Path:
    if isinstance(path, str):
        path = path.strip()
        if path.startswith(":"):
            path = path[1:]
            handle, resource = path.split(":")
            while resource.startswith("/") or resource.startswith("\\"):
                resource = resource[1:]

            try:
                handle_path = resource_handles[handle]
            except KeyError:
                raise KeyError(f'Unknown resource handle "{handle}"')

            path = Path(handle_path / resource)
        else:
            path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Cannot locate resource: {path}")

    return path.resolve()


def add_resource_handle(handle: str, path: Union[str, Path]) -> None:
    if isinstance(path, str):
        path = Path(path).resolve()
    elif isinstance(path, Path):
        path = path.resolve()
    else:
        raise TypeError("Path for resource handle must be a string or Path object")

    if not path.is_absolute():
        raise RuntimeError(
            "Path for resource handle must be absolute. "
            "See https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve"
        )

    if not path.exists():
        raise FileNotFoundError(f"Cannot locate location for handle: {path}")

    resource_handles[handle] = path
