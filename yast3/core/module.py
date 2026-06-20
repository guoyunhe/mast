"""Base module class for YaST3 modules."""


class Module:
    """Base class for YaST3 modules."""

    name: str
    icon_names: tuple[str, ...]

    def __init__(self, name: str, icon_names: tuple[str, ...]):
        self.name = name
        self.icon_names = icon_names

    def launch(self) -> None:
        """Launch the module window."""
        raise NotImplementedError("Module launch not implemented.")