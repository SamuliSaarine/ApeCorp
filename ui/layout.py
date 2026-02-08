from fasthtml.common import Titled, Main, Style

def Layout(title="JonesCorp", *components):
    return Titled(title,
        Main(
            *components,
            cls="container-fluid"
        ),
        # Basic styling for the grid
        Style("""
            :root {
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --border-color: #333;
                --accent-color: #00ff00;
            }
            body { 
                background-color: var(--bg-color); 
                color: var(--text-color); 
                font-family: monospace;
                margin: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .container-fluid {
                display: grid;
                grid-template-columns: 300px 1fr;
                grid-template-rows: 1fr 100px;
                gap: 10px;
                padding: 10px;
                height: 100%;
                box-sizing: border-box;
            }
            .window {
                border: 1px solid var(--border-color);
                border-radius: 4px;
                padding: 10px;
                background: #222;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            .window-title {
                border-bottom: 1px solid var(--border-color);
                margin-bottom: 5px;
                padding-bottom: 5px;
                font-weight: bold;
                color: var(--accent-color);
            }
            #info-window { grid-column: 1; grid-row: 1 / span 2; }
            #log-window { grid-column: 2; grid-row: 1; overflow-y: auto; }
            #whisper-window { grid-column: 2; grid-row: 2; }
            
            input[type="text"] {
                width: 100%;
                background: #333;
                border: 1px solid var(--border-color);
                color: white;
                padding: 8px;
                font-family: monospace;
            }
            button {
                background: var(--border-color);
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
            }
            button:hover { background: #444; }
        """)
    )
