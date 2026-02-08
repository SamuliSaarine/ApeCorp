from fasthtml.common import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Tribe

def ui_view(tribe: 'Tribe'):
    return Div(
        H3(f"Tribe: {tribe.name}", cls="border-b border-gray-600 mb-2 pb-1"),
        Div(
            P(Strong("Territory: "), tribe.territory),
            P(Strong("Culture: "), tribe.culture),
            P(Strong("Survival Strategy: "), tribe.survival_strategy),
            cls="mb-4"
        ),
        Div(
            H4("Challenges", cls="bold"),
            Ul(*[Li(c) for c in tribe.challenges], cls="pl-4 list-disc"),
            cls="mb-4"
        ),
        Div(
            H4("Relations", cls="bold"),
            P(tribe.tribe_relations),
        ),
        cls="p-2"
    )
