from pathlib import Path


def project_root_from_config(config_path: str | Path) -> Path:
    config_path = Path(config_path).resolve()
    return (
        config_path.parent.parent
        if config_path.parent.name == "config"
        else config_path.parent
    )


def resolve_under_root(config_path: str | Path, maybe_path: str | Path) -> Path:
    p = Path(maybe_path)
    if p.is_absolute():
        return p
    root = project_root_from_config(config_path)
    return (root / p).resolve()


__all__ = ["project_root_from_config", "resolve_under_root"]

