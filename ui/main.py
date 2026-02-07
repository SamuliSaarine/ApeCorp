from fasthtml.common import *
import asyncio, random, logging, time
from typing import Callable
import json


class PermanentAPIError(Exception):
    """Raised when the remote model service reports a non-transient capacity/credits error."""
    pass

# Logger for UI server-side events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ui")
from actors.world import World
from actors.tribe import Tribe
from actors.ape import Ape
from actors import player, ape
from pydantic_ai.exceptions import ModelHTTPError

# --- 1. HEADERS & CSS FIXES ---
tlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")
style = Style("""
    .map-placeholder { background: repeating-conic-gradient(#1a2e1a 0% 25%, #142414 0% 50%) 50% / 40px 40px; }
    .profile-placeholder { background: linear-gradient(45deg, #111 25%, #1a1a1a 25%, #1a1a1a 50%, #111 50%); background-size: 10px 10px; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    
    /* Panel & Tab Fixes */
    .game-panel { border-radius: 1.5rem; overflow: hidden; border: 1px solid #27272a; display: flex; flex-direction: column; }
    .tab-container { border-top-left-radius: 1.5rem; border-top-right-radius: 1.5rem; overflow: hidden; }
    
    /* Height & Input Sync */
    .footer-input { height: 3.5rem; }
    
    /* HTMX Indicator */
    .htmx-indicator { display: none; }
    .htmx-request .htmx-indicator { display: inline; }
    .htmx-request.execute-btn { opacity: 0.8; cursor: wait; animation: pulse-cyan 1.5s infinite; }
    
    @keyframes pulse-cyan {
        0%, 100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7); }
        50% { box-shadow: 0 0 0 10px rgba(6, 182, 212, 0); }
    }
        /* Polling indicator */
        .polling { display: none; }
    @keyframes pulse-soft { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        /* Script for polling state changes */
    .moving-npc { animation: pulse-soft 2s infinite; }
""")

app, rt = fast_app(hdrs=(tlink, style))

# --- 2. STATE & GAME INITIALIZATION ---
# Game state
G = {
    "resources": {"Wood": 140, "Meat": 85, "Morale": "Stable"},
    "season": "Frost", "day": 12, "time": "21:45",
    "targets": [{"id": "global", "label": "World (Global)"}, {"id": "n1", "label": "Hunter Jace"}, {"id": "c1", "label": "Ancient Cave"}],
    "actions": ["Hunt", "Build", "Scout", "Rest"],
    "npcs": [{"id": "n1", "name": "Hunter Jace", "x": 35, "y": 45, "type": "npc"}, {"id": "p1", "name": "Chief", "x": 50, "y": 50, "type": "player"}]
}

# Engine initialization state
engine_state = {
    "pending_options": None,
    "selection_event": None,
    "selected_index": None,
    "current_stage": "idle",  # idle, world_gen, tribe_gen, ape_selection
    "selection_title": None,
    "selection_description": None,
    "game_started": False
}

PANELS = {
    "player": {"active_id": "stats", "tabs": [{"id": "stats", "label": "Character", "closable": False, "data": "Level 10 Tribal Leader"}]},
    "inspector": {"active_id": "log", "tabs": [{"id": "log", "label": "System Log", "closable": False, "data": "Awaiting agent instructions..."}]}
}

def create_web_selector():
    """Create a selector function that collects selections from web UI"""
    async def web_selector(options):
        # Set the options to be displayed
        engine_state["pending_options"] = options
        engine_state["selection_event"] = asyncio.Event()
        engine_state["selected_index"] = None
        
        # Determine what stage we're at
        if engine_state["current_stage"] == "world_gen":
            engine_state["selection_title"] = "Choose Your World"
            engine_state["selection_description"] = "Select the world type for your tribe"
        elif engine_state["current_stage"] == "tribe_gen":
            engine_state["selection_title"] = "Choose Your Tribe"
            engine_state["selection_description"] = "Select your tribe's culture and values"
        elif engine_state["current_stage"] == "ape_selection":
            engine_state["selection_title"] = "Select Your Character"
            engine_state["selection_description"] = "Choose which ape will be your player character"
        
        # Wait for user selection via web UI
        logger.info("web_selector waiting: %d options (stage=%s)", len(options), engine_state.get("current_stage"))
        await engine_state["selection_event"].wait()
        logger.info("web_selector received selection: %s", engine_state.get("selected_index"))
        return engine_state["selected_index"]
    return web_selector

# Background task for running the game engine
game_task = None

async def run_game_engine():
    """Run the game engine with web-based selections"""
    global game_task
    try:
        selector = create_web_selector()
        logger.info("Game engine started")

        async def _with_retries(call_factory: Callable[[], asyncio.Future], name: str, retries: int = 3, base_delay: float = 1.0):
            """Call an async factory with retries/backoff on ModelHTTPError 429 responses."""
            for attempt in range(1, retries + 1):
                try:
                    return await call_factory()
                except ModelHTTPError as e:
                    status = getattr(e, "status_code", None)
                    logger.warning("%s failed with ModelHTTPError (status=%s) attempt %d/%d", name, status, attempt, retries)
                    # Try to parse the error body and detect permanent capacity/credits issues
                    body_text = getattr(e, "body", None)
                    body = {}
                    if body_text:
                        try:
                            body = json.loads(body_text)
                        except Exception:
                            body = {}

                    error_type = body.get("type") or body.get("code") or body.get("message")
                    # Known permanent error from Mistral/pydantic_ai: service_tier_capacity_exceeded / code 3505
                    if error_type in ("service_tier_capacity_exceeded", "3505") or (isinstance(error_type, str) and "capacity" in error_type.lower()):
                        logger.error("Permanent capacity/credits error detected from model: %s", body)
                        raise PermanentAPIError(body.get("message") or "Model service capacity exceeded / out of credits") from e

                    # If rate-limited, apply exponential backoff and retry
                    if status == 429 and attempt < retries:
                        delay = base_delay * (2 ** (attempt - 1)) + random.random() * 0.5
                        logger.info("Retrying %s after %.2fs due to 429", name, delay)
                        await asyncio.sleep(delay)
                        continue
                    # Not retryable or out of attempts: re-raise
                    raise

        engine_state["current_stage"] = "world_gen"
        await _with_retries(lambda: World.generate(selector), "World.generate")
        logger.info("World generated")

        engine_state["current_stage"] = "tribe_gen"
        await _with_retries(lambda: Tribe.generate(selector), "Tribe.generate")
        logger.info("Tribe generated")

        engine_state["current_stage"] = "ape_selection"
        await _with_retries(lambda: Ape.generate(), "Ape.generate")
        logger.info("Apes generated")
        
        # Let user select their player ape
        ape_options = [a.view() for a in ape.instances]
        selected_ape_idx = await selector(ape_options)
        player.instance = ape.instances[selected_ape_idx]
        
        # Game initialized successfully
        engine_state["game_started"] = True
        engine_state["pending_options"] = None
        message = f"Game initialized! You are {player.instance.name}. Ready to command."
        PANELS["inspector"]["tabs"].append({
            "id": "game_started",
            "label": "Game Start",
            "closable": False,
            "data": message
        })
        PANELS["inspector"]["active_id"] = "game_started"
    except Exception as e:
        logger.exception("Error in game engine")
        error_msg = f"Error initializing game: {str(e)}"
        engine_state["pending_options"] = None
        PANELS["inspector"]["tabs"].append({
            "id": "error",
            "label": "Error",
            "closable": True,
            "data": error_msg
        })
        PANELS["inspector"]["active_id"] = "error"
    finally:
        game_task = None

# --- 3. COMPONENTS ---

def TabHeader(panel_id, tab, is_active):
    active_cls = "border-b-2 border-cyan-500 text-white bg-zinc-800" if is_active else "text-zinc-500 hover:text-zinc-300"
    close_btn = Span(" ×", cls="ml-2 hover:text-red-500", hx_post=f"/close-tab/{panel_id}/{tab['id']}", hx_target=f"#{panel_id}-panel", hx_swap="outerHTML") if tab['closable'] else ""
    return Button(Span(tab['label']), close_btn, cls=f"px-4 py-3 text-[10px] uppercase tracking-widest transition-all {active_cls}",
                  hx_get=f"/switch-tab/{panel_id}/{tab['id']}", hx_target=f"#{panel_id}-panel", hx_swap="outerHTML")

def TabbedPanel(panel_id):
    state = PANELS[panel_id]
    active_tab = next((t for t in state['tabs'] if t['id'] == state['active_id']), state['tabs'][0])
    return Div(
        # Tab bar with rounded-t matching parent
        Div(*[TabHeader(panel_id, t, t['id'] == state['active_id']) for t in state['tabs']], 
            cls="flex bg-black border-b border-zinc-800 overflow-x-auto no-scrollbar tab-container"),
        Div(
            Div(cls="w-full h-40 mb-4 profile-placeholder rounded-xl border border-zinc-800"),
            P(active_tab['data'], cls="text-sm text-zinc-400 italic leading-relaxed"),
            cls="p-5 flex-grow"
        ),
        id=f"{panel_id}-panel", cls="bg-zinc-900 game-panel h-full"
    )

def PromptFooter():
    options = [Option(t['label'], value=t['id']) for t in G['targets']]
    
    # Combined Action Buttons + Prompt Box
    return Footer(
        # Row 1: Suggested Action Buttons
        Div(*[Button(a, cls="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-[10px] uppercase tracking-widest px-4 py-1 rounded-full border border-zinc-700 transition") for a in G['actions']], 
            cls="flex gap-2 mb-4 px-2"),
        
        # Row 2: Prompt + Target + Execute
        Form(
            Input(name="cmd", placeholder="Enter command...", 
                  cls="footer-input flex-grow bg-zinc-900 border-l border-y border-zinc-700 px-6 text-white focus:outline-none rounded-l-2xl"),
            
            # Using Flex on Select wrapper to force height matching
            Div(Select(*options, name="target_id", 
                       cls="footer-input bg-zinc-800 text-cyan-400 border border-zinc-700 px-4 focus:outline-none w-48 appearance-none"),
                cls="relative flex items-center"),
            
            Button(Span("EXECUTE", cls="button-text"), 
                   Span("Thinking...", cls="htmx-indicator ml-2 italic text-xs animate-pulse"),
                   cls="footer-input execute-btn bg-cyan-600 hover:bg-cyan-500 text-white font-black px-10 rounded-r-2xl flex items-center justify-center min-w-[180px]", 
                   id="submit-btn"),
            
            cls="flex w-full items-stretch shadow-2xl", hx_post="/execute-command", hx_target="#inspector-panel", hx_swap="outerHTML", hx_indicator="#submit-btn"
        ), 
        cls="p-6 bg-[#050505] w-full max-w-6xl mx-auto"
    )

# --- 4. LAYOUT & ROUTES ---

def landing_page():
    """Landing page with start button"""
    return Title("The Last Tribe"), Main(
        Div(
            Div(
                H1("THE LAST TRIBE", cls="font-black text-6xl mb-4 tracking-tighter text-white"),
                P("An AI-driven tribal survival experience", cls="text-xl text-zinc-400 mb-8"),
                Button(
                    "START GAME",
                    id="start-btn",
                    cls="bg-cyan-600 hover:bg-cyan-500 text-white font-black px-12 py-4 rounded-lg text-lg transition-all",
                    hx_post="/init-game",
                    hx_target="body",
                    hx_swap="outerHTML",
                    hx_indicator="#start-btn"
                ),
                cls="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-zinc-900 to-black text-center"
            ),
            cls="w-full"
        )
    )

@rt("/poll-state")
def get_poll_state():
    """Endpoint to check and return current UI state"""
    start = time.time()
    logger.info("/poll-state called; stage=%s pending=%s", engine_state.get("current_stage"), bool(engine_state.get("pending_options")))
    try:
        if engine_state["game_started"]:
            return game_page()
        elif engine_state["pending_options"]:
            return selection_page()
        else:
            # Still loading, return empty or same landing
            return ""
    finally:
        dur = (time.time() - start) * 1000
        logger.info("/poll-state handled in %.1fms", dur)
def game_page():
    """Main game page with panels and controls"""
    return Title("Tribe Engine"), Main(
        Header(
            Div(H1("THE LAST TRIBE", cls="font-black text-2xl tracking-tighter"), p="Alpha-Demo", cls="flex items-baseline gap-3"),
            Div(*[Div(f"{k}: {v}", cls="bg-zinc-900 px-4 py-1 rounded-full border border-zinc-800 text-xs font-bold text-cyan-500") for k,v in G['resources'].items()], cls="flex gap-4"),
            Div(f"❄️ {G['season']} | Day {G['day']} | 🕒 {G['time']}", cls="text-zinc-400 font-mono text-sm bg-zinc-900 px-4 py-1 rounded-full border border-zinc-800"),
            cls="flex justify-between items-center p-6 bg-[#050505]"
        ),
        Div(
            Div(
                Div(cls="absolute inset-0 map-placeholder opacity-40"),
                Div(id="npc-layer", hx_ext="sse", sse_connect="/live-movements", sse_swap="message"),
                cls="col-span-6 relative h-full game-panel bg-black"
            ),
            Div(TabbedPanel("player"), cls="col-span-2 p-2 h-full"),
            Div(TabbedPanel("inspector"), cls="col-span-2 p-2 h-full"),
            cls="grid grid-cols-10 h-[calc(100vh-220px)] px-4"
        ),
        PromptFooter(),
        cls="h-screen flex flex-col bg-[#050505] text-zinc-200 overflow-hidden"
    )

def selection_page():
    """Page showing side-by-side selection options"""
    options = engine_state["pending_options"] or []
    title = engine_state["selection_title"] or "Make a Selection"
    description = engine_state["selection_description"] or ""
    
    return Div(
        Div(
            H2(title, cls="font-black text-4xl mb-2 text-white"),
            P(description, cls="text-lg text-zinc-400 mb-8"),
            Div(
                *[Div(
                    Button(
                        option,
                        cls="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-8 px-6 rounded-lg text-center transition-all h-full",
                        hx_post=f"/select-option/{idx}",
                        hx_target="body",
                        hx_swap="outerHTML"
                    ),
                    cls="flex-1"
                ) for idx, option in enumerate(options)],
                cls="flex gap-6 w-full"
            ),
            cls="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-zinc-900 to-black text-center px-8"
        ),
        cls="w-full"
    )

@rt("/")
def index():
    if engine_state["game_started"]:
        return game_page()
    elif engine_state["pending_options"]:
        return selection_page()
    else:
        return landing_page()

@rt("/favicon.ico")
def favicon():
    """Return empty response to avoid 404 errors"""
    return ""

@rt("/live-movements")
async def sse_movements():
    async def event_generator():
        while True:
            for npc in G['npcs']:
                npc['x'] = max(2, min(98, npc['x'] + random.uniform(-0.4, 0.4)))
                npc['y'] = max(2, min(98, npc['y'] + random.uniform(-0.4, 0.4)))
            markers = [Div("▲" if n['type']=='player' else "◆", cls=f"absolute text-2xl cursor-pointer moving-npc {'text-white' if n['type']=='player' else 'text-cyan-500'}",
                           style=f"left:{n['x']}%; top:{n['y']}%; transition: all 1s linear;", hx_get=f"/open-tab/{n['name']}", hx_target="#inspector-panel", hx_swap="outerHTML") for n in G['npcs']]
            yield f"data: {to_xml(Div(*markers, id='npc-layer'))}\n\n"
            await asyncio.sleep(1)
    return EventStream(event_generator())

@rt("/switch-tab/{panel_id}/{tab_id}")
def get(panel_id: str, tab_id: str):
    PANELS[panel_id]['active_id'] = tab_id
    return TabbedPanel(panel_id)

@rt("/close-tab/{panel_id}/{tab_id}")
def post(panel_id: str, tab_id: str):
    PANELS[panel_id]['tabs'] = [t for t in PANELS[panel_id]['tabs'] if t['id'] != tab_id]
    PANELS[panel_id]['active_id'] = PANELS[panel_id]['tabs'][0]['id']
    return TabbedPanel(panel_id)

@rt("/open-tab/{name}")
def get(name: str):
    tab_id = name.lower().replace(" ", "_")
    if not any(t['id'] == tab_id for t in PANELS['inspector']['tabs']):
        PANELS['inspector']['tabs'].append({"id": tab_id, "label": name, "closable": True, "data": f"Inspecting {name}. Scanning vital signs..."})
    PANELS['inspector']['active_id'] = tab_id
    return TabbedPanel("inspector")

@rt("/execute-command")
async def post(cmd: str, target_id: str):
    await asyncio.sleep(1.2)
    label = next((t['label'] for t in G['targets'] if t['id'] == target_id), "Unknown")
    tid = f"re_{random.randint(100,999)}"
    PANELS["inspector"]["tabs"].append({"id": tid, "label": f"RE: {label}", "closable": True, "data": f"The command '{cmd}' has been analyzed. Result: Successful."})
    PANELS["inspector"]["active_id"] = tid
    return TabbedPanel("inspector")

@rt("/init-game")
async def post():
    """Start the game initialization process: kick off background task and return loading UI"""
    global game_task
    if not game_task:
        game_task = asyncio.create_task(run_game_engine())

    # Return an immediate loading fragment so user sees feedback
    return Div(
        Div(
            H2("Initializing game...", cls="text-2xl font-black text-white mb-4"),
            P("Please wait — the world and tribe are being generated.", cls="text-zinc-400 mb-6"),
            Div("", cls="polling", hx_get="/poll-state", hx_trigger="every 1s", hx_target="body", hx_swap="outerHTML"),
            cls="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-zinc-900 to-black text-center px-8"
        ),
        cls="w-full"
    )

@rt("/select-option/{option_index:int}")
def post(option_index: int):
    """Handle selection from UI for World/Tribe/Ape generation"""
    logger.info("/select-option called: %s", option_index)
    if engine_state["selection_event"]:
        engine_state["selected_index"] = option_index
        engine_state["selection_event"].set()
    
    # Return the appropriate page based on current state
    if engine_state["game_started"]:
        return game_page()
    elif engine_state["pending_options"]:
        return selection_page()
    else:
        return landing_page()

async def run_ui():
    """Run the fastHTML application"""
    import uvicorn
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()