import os
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

from arguebuf.schemas.d2 import D2Graph

__all__ = ("d2",)
FORMATS = ["png", "pdf", "svg"]


def d2(
    graph: D2Graph,
    path: Path | str,
) -> None:
    """Visualize a Graph instance using a D2 backend. Make sure that a D2 Executable path is set on your machine for visualization."""

    if isinstance(path, str):
        path = Path(path)

    if path.suffix.removeprefix(".") not in FORMATS:
        raise ValueError(
            f"You need to provide a path with a file ending supported by d2: {FORMATS}"
        )

    # Create temporary file
    tmp = NamedTemporaryFile(delete=False, mode="w")
    try:
        tmp.write(str(graph))
    finally:
        tmp.close()
        # run d2 command and produce the output file
        run(["d2", tmp.name, str(path)])
        # remove temporary file
        os.unlink(tmp.name)
