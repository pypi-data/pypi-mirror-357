"""RFC 7807 Problem exception and middleware"""

from typing import Any, Dict


class Problem(Exception):
    """An RFC 7807 Problem exception."""

    def __init__(
        self,
        type: str,
        title: str,
        status: int,
        detail: str,
        instance: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize the Problem exception."""
        self.type: str = type
        self.status: int = status
        self.title: str = title
        self.detail: str = detail
        self.instance: str | None = instance
        self.kwargs: Dict = kwargs

    def __str__(self) -> str:
        """Return a string representation of the Problem exception."""
        return str(f"Problem:<{self.to_dict()}>")

    def __repr__(self) -> str:
        """Return a string representation of the Problem exception."""
        return str(self)

    def to_dict(self) -> Dict[str, Any]:
        """Get a dictionary representation of the Problem response."""
        d = {}
        d.update(self.kwargs)

        if self.type:
            d["type"] = str(self.type)
        if self.title:
            d["title"] = str(self.title)
        if self.status:
            d["status"] = int(self.status)
        if self.detail:
            d["detail"] = str(self.detail)
        if self.instance:
            d["instance"] = str(self.instance)
        return d
