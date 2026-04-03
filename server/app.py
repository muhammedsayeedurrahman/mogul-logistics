"""FastAPI application - entry point for the environment server."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi.responses import RedirectResponse
from openenv.core.env_server import create_app

from models import ShipmentAction, ShipmentObservation
from server.environment import ShipmentEnvironment
from server.gradio_custom import build_custom_dashboard

app = create_app(
    ShipmentEnvironment,
    ShipmentAction,
    ShipmentObservation,
    env_name="mogul-logistics",
    max_concurrent_envs=1,
    gradio_builder=build_custom_dashboard,
)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to the web interface."""
    return RedirectResponse(url="/web")


def main() -> None:
    """Run the server directly via `python -m server.app` or `uv run server`."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
