from fasthtml.common import Div, Form, Input, Button

def WhisperWindow():
    return Div(
        Div("Whisper Link", cls="window-title"),
        Form(
            Input(type="text", name="msg", placeholder="Whisper to player...", autofocus=True),
            Button("Send", type="submit"),
            hx_post="/whisper",
            hx_target="#log-content",
            hx_swap="beforeend",
            # Clear input after sending
            hx_on__after_request="this.reset()",
            cls="flex gap-2"
        ),
        id="whisper-window",
        cls="window"
    )
