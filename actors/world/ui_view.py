from fasthtml.common import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import World

def ui_view(world: 'World'):
    territories_html = [
        Div(
            H4(t.name, cls="text-accent"),
            P(t.description),
            P(f"Resources: {', '.join(t.resources)}", cls="text-sm text-muted"),
            cls="mb-4 p-2 border border-gray-700 rounded"
        ) for t in world.territories
    ]
    
    return Div(
        H3("World: The Valley", cls="border-b border-gray-600 mb-2 pb-1"),
        P(world.description, cls="mb-4"),
        H4("Territories", cls="bold mt-2"),
        *territories_html,
        cls="p-2"
    )
