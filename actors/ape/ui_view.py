from fasthtml.common import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Ape

def ui_view(ape: 'Ape'):
    return Div(
        H3(f"Ape: {ape.name}", cls="border-b border-gray-600 mb-2 pb-1 text-xl"),
        Div(
            P(Strong("Age: "), ape.age, Span(" | "), Strong("Gender: "), ape.gender),
            P(Strong("Role: "), ape.role),
            cls="mb-4"
        ),
        Div(
            H4("Personality", cls="bold text-accent"),
            P(str(ape.personality)),
            cls="mb-4"
        ),
        Div(
            H4("Facts", cls="bold text-accent"),
            Ul(*[Li(f) for f in ape.facts], cls="pl-4 list-disc"),
            cls="mb-4"
        ),
        Div(
            H4("Opinions", cls="bold text-accent"),
            Ul(*[Li(o) for o in ape.opinions], cls="pl-4 list-disc"),
            cls="mb-4"
        ),
        cls="p-2"
    )
