class CallableAttr:
    def __str__(self) -> str:
        return f"CallableAttr({self.name}, {self.args}, {self.kwargs})"

    def __repr__(self) -> str:
        return str(self)

    def __init__(self, name: str, *args: object, **kwargs) -> None:
        self.name = name
        self.args = args
        self.kwargs = kwargs


def tryget(obj: object, *attrs: str | CallableAttr) -> object | None:
    accessed = obj
    for attr in attrs:
        if isinstance(attr, str):
            accessed = getattr(accessed, attr, None)
        elif isinstance(attr, CallableAttr):
            accessed = getattr(accessed, attr.name, None)
            if accessed is not None:
                assert callable(accessed)
                accessed = accessed(*attr.args, **attr.kwargs)
        else:
            assert (), f"invalid type {type(attr)}"

    return accessed
