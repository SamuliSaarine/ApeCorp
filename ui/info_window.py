from fasthtml.common import Div, A

def InfoWindow(content, section="ape"):
    # Tabs
    tabs = Div(
        A("Ape", href="#", hx_get="/info/ape", hx_target="#info-content", cls="tab" + (" active" if section == "ape" else "")),
        A("Tribe", href="#", hx_get="/info/tribe", hx_target="#info-content", cls="tab" + (" active" if section == "tribe" else "")),
        A("World", href="#", hx_get="/info/world", hx_target="#info-content", cls="tab" + (" active" if section == "world" else "")),
        cls="tabs flex space-x-2 border-b border-gray-600 mb-2"
    )

    return Div(
        Div("Status", cls="window-title"),
        tabs,
        Div(
            content,
            id="info-content",
            hx_get=f"/info/{section}", 
            hx_trigger="every 2s",
            cls="h-full overflow-y-auto"
        ),
        id="info-window",
        cls="window"
    )
