from typing import TypeAlias
from ui.layout import Layout
from ui.log_window import LogWindow, LogMessage
from ui.whisper_window import WhisperWindow
from ui.info_window import InfoWindow
from fasthtml.common import *

InterfaceType: TypeAlias = str

def ask_user_choice(options: list[InterfaceType]) -> int:
    # Legacy CLI method, arguably unused in web mode or needs adaptation
    for i, option in enumerate(options):
        print(f"{i})\n{option}\n")
    choice = input("Choose an option: ")
    return int(choice)

def render_app(player):
    """
    Renders the main application layout.
    """
    player_info = render_info(player, "ape")
    return Layout("JonesCorp Mission",
        player_info,
        LogWindow(),
        WhisperWindow()
    )

def render_log(msg: str):
    """
    Renders a single log message.
    """
    return LogMessage(msg)

def render_info(player, section="ape"):
    """
    Renders the updated info window content based on section.
    """
    from fasthtml.common import Div
    if not player or not player.ape:
        return InfoWindow("Initializing...", section)

    if section == "world":
        from actors.world.ui_view import ui_view
        from actors import world
        content = ui_view(world.instance) if world.instance else Div("Unknown World")
    elif section == "tribe":
        from actors.tribe.ui_view import ui_view
        from actors import tribe
        content = ui_view(tribe.instance) if tribe.instance else Div("Unknown Tribe")
    else: # Ape by default
        from actors.ape.ui_view import ui_view
        content = ui_view(player.ape)

    # For OOB updates or direct renders, we might want just the content if triggered by polling the content div
    # But if we re-render the whole window (initial load), we need Tabs.
    # The Polling endpoint /info/{section} likely targets #info-content, so we return JUST content?
    # Actually, let's make render_info return the WHOLE window structure for initial load, 
    # and maybe a helper for just content? 
    # Wait, the polling replaces #info-content. So we should return only content here?
    # BUT render_app calls render_info for initial load.
    
    # Let's split it. render_info_content vs render_info_window
    return InfoWindow(content, section)

def render_info_content(player, section="ape"):
    from fasthtml.common import Div
    if not player or not player.ape:
        return Div("Initializing...")

    if section == "world":
        from actors.world.ui_view import ui_view
        from actors import world
        return ui_view(world.instance) if world.instance else Div("World not ready")
    elif section == "tribe":
        from actors.tribe.ui_view import ui_view
        from actors import tribe
        return ui_view(tribe.instance) if tribe.instance else Div("Tribe not ready")
    else:
        from actors.ape.ui_view import ui_view
        return ui_view(player.ape)