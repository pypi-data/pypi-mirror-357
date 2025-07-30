#!/usr/bin/env python3
"""
Demo showing audio widget placement options in VME chat app
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Header, Footer

from src.clients.textual_cli.ui.simple_audio_widgets import (
    MicrophoneWidget, 
    SimpleAudioBar,
    AudioState
)

class AudioLayoutDemo(App):
    """Demo app showing different audio widget placement options"""
    
    CSS = """
    Screen {
        background: #0d1117;
    }
    
    #chat-area {
        background: #161b22;
        padding: 0 2;
        height: 1fr;
        border: solid #30363d;
        margin: 1;
    }
    
    #input-container {
        background: #161b22;
        padding: 1 2;
        height: 5;
        dock: bottom;
        border-top: solid #30363d;
    }
    
    #audio-status-bar {
        dock: top;
        height: 1;
        background: #21262d;
        border-bottom: solid #30363d;
    }
    
    #audio-panel {
        dock: bottom;
        height: 6;
        background: #161b22;
        border-top: solid #30363d;
        padding: 1;
    }
    
    Input {
        color: white;
        background: #0d1117;
        border: solid #30363d;
    }
    
    Input:focus {
        border: solid #58a6ff;
    }
    """
    
    def compose(self) -> ComposeResult:
        # OPTION 1: Audio status in top bar (minimal)
        yield SimpleAudioBar(id="audio-status-bar")
        
        yield Header(show_clock=False)
        
        # Main chat area
        with Container(id="chat-area"):
            yield Static("Chat messages would go here...\n" * 10)
        
        # OPTION 2: Audio panel above input (prominent)
        with Container(id="audio-panel"):
            with Horizontal():
                yield MicrophoneWidget(id="mic")
                with Vertical():
                    yield Static("🔗 OpenAI Realtime API", id="connection-status")
                    yield Static("WebSocket connection for voice chat", id="connection-detail")
        
        # Input area
        with Container(id="input-container"):
            yield Static("💬 Type or speak your message:")
            yield Input(placeholder="Ask about VME infrastructure...", id="chat-input")
        
        yield Footer()
    
    async def on_mount(self):
        """Demo the audio widgets"""
        mic = self.query_one("#mic", MicrophoneWidget)
        status_bar = self.query_one("#audio-status-bar", SimpleAudioBar)
        
        # Show different states
        await asyncio.sleep(1)
        
        # Listening state
        mic.set_state(AudioState.LISTENING, 0.4)
        status_bar.update_audio_state(AudioState.LISTENING)
        status_bar.update_connection_state("connected")
        await asyncio.sleep(3)
        
        # Speaking state  
        mic.set_state(AudioState.SPEAKING, 0.8)
        status_bar.update_audio_state(AudioState.SPEAKING)
        await asyncio.sleep(2)

if __name__ == "__main__":
    app = AudioLayoutDemo()
    app.run()