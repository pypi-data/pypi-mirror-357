import tomlkit


def toml_loads(string: str | bytes) -> tomlkit.TOMLDocument:
    return tomlkit.loads(string)
