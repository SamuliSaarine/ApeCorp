from fasthtml.common import Div

def LogWindow():
    return Div(
        Div("Mission Log", cls="window-title"),
        Div(
            id="log-content",
            hx_get="/log_updates",
            hx_trigger="every 1s",
            cls="h-full overflow-y-auto"
        ),
        id="log-window",
        cls="window"
    )

def LogMessage(msg: str):
    """Returns a single log message element"""
    return Div(f"> {msg}", cls="log-message")
