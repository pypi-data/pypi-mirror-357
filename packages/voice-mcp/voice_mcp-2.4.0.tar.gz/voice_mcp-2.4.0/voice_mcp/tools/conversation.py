"""Conversation tools for interactive voice interactions."""

import asyncio
import logging
import os
import time
import traceback
from typing import Optional, Literal, Tuple
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from openai import AsyncOpenAI
import httpx

from voice_mcp.server import mcp
from voice_mcp.config import (
    audio_operation_lock,
    SAMPLE_RATE,
    CHANNELS,
    DEBUG,
    DEBUG_DIR,
    SAVE_AUDIO,
    AUDIO_DIR,
    OPENAI_API_KEY,
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    PREFER_LOCAL,
    AUDIO_FEEDBACK_ENABLED,
    service_processes,
    HTTP_CLIENT_CONFIG
)
import voice_mcp.config
from voice_mcp.providers import (
    get_tts_client_and_voice,
    get_stt_client,
    is_provider_available,
    get_provider_by_voice,
    select_best_voice
)
from voice_mcp.provider_discovery import provider_registry
from voice_mcp.core import (
    get_openai_clients,
    text_to_speech,
    cleanup as cleanup_clients,
    save_debug_file,
    get_debug_filename,
    play_chime_start,
    play_chime_end
)
from voice_mcp.tools.statistics import track_voice_interaction
from voice_mcp.utils import (
    get_event_logger,
    log_recording_start,
    log_recording_end,
    log_stt_start,
    log_stt_complete,
    log_tool_request_start,
    log_tool_request_end
)

logger = logging.getLogger("voice-mcp")

# Track last session end time for measuring AI thinking time
last_session_end_time = None

# Initialize OpenAI clients - now using provider registry for endpoint discovery
openai_clients = get_openai_clients(OPENAI_API_KEY, None, None)

# Provider-specific clients are now created dynamically by the provider registry


async def startup_initialization():
    """Initialize services on startup based on configuration"""
    if voice_mcp.config._startup_initialized:
        return
    
    voice_mcp.config._startup_initialized = True
    logger.info("Running startup initialization...")
    
    # Initialize provider registry
    logger.info("Initializing provider registry...")
    await provider_registry.initialize()
    
    # Check if we should auto-start Kokoro
    auto_start_kokoro = os.getenv("VOICE_MCP_AUTO_START_KOKORO", "").lower() in ("true", "1", "yes", "on")
    if auto_start_kokoro:
        try:
            # Check if Kokoro is already running
            async with httpx.AsyncClient(timeout=3.0) as client:
                base_url = 'http://studio:8880'  # Kokoro default
                health_url = f"{base_url}/health"
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    logger.info("Kokoro TTS is already running externally")
                else:
                    raise Exception("Not running")
        except:
            # Kokoro is not running, start it
            logger.info("Auto-starting Kokoro TTS service...")
            try:
                # Import here to avoid circular dependency
                import subprocess
                if "kokoro" not in service_processes:
                    process = subprocess.Popen(
                        ["uvx", "kokoro-fastapi"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env={**os.environ}
                    )
                    service_processes["kokoro"] = process
                    
                    # Wait a moment for it to start
                    await asyncio.sleep(2.0)
                    
                    # Verify it started
                    if process.poll() is None:
                        logger.info(f"✓ Kokoro TTS started successfully (PID: {process.pid})")
                    else:
                        logger.error("Failed to start Kokoro TTS")
            except Exception as e:
                logger.error(f"Error auto-starting Kokoro: {e}")
    
    # Log initial status
    logger.info("Service initialization complete")


async def get_tts_config(provider: Optional[str] = None, voice: Optional[str] = None, model: Optional[str] = None, instructions: Optional[str] = None):
    """Get TTS configuration based on provider selection"""
    # Validate instructions usage
    if instructions and model != "gpt-4o-mini-tts":
        logger.warning(f"Instructions parameter is only supported with gpt-4o-mini-tts model, ignoring for model: {model}")
        instructions = None
    
    # Map provider names to base URLs
    provider_urls = {
        'openai': 'https://api.openai.com/v1',
        'kokoro': 'http://studio:8880/v1'
    }
    
    # Convert provider name to URL if it's a known provider
    base_url = provider_urls.get(provider, provider)
    
    # Use new provider selection logic
    try:
        client, selected_voice, selected_model, endpoint_info = await get_tts_client_and_voice(
            voice=voice,
            model=model,
            base_url=base_url  # Now using mapped URL
        )
        
        # Return configuration compatible with existing code
        return {
            'client': client,
            'base_url': endpoint_info.url,
            'model': selected_model,
            'voice': selected_voice,
            'instructions': instructions,
            'provider': endpoint_info.url  # For logging
        }
    except Exception as e:
        logger.error(f"Failed to get TTS client: {e}")
        # Fallback to legacy behavior
        return {
            'client_key': 'tts',
            'base_url': 'https://api.openai.com/v1',  # Fallback to OpenAI
            'model': model or 'tts-1',
            'voice': voice or 'alloy',
            'instructions': instructions
        }


async def get_stt_config(provider: Optional[str] = None):
    """Get STT configuration based on provider selection"""
    try:
        # Use new provider selection logic
        client, selected_model, endpoint_info = await get_stt_client(
            model=None,  # Let system select
            base_url=provider  # Allow provider to be a base URL
        )
        
        return {
            'client': client,
            'base_url': endpoint_info.url,
            'model': selected_model,
            'provider': endpoint_info.url  # For logging
        }
    except Exception as e:
        logger.error(f"Failed to get STT client: {e}")
        # Fallback to legacy behavior
        return {
            'client_key': 'stt',
            'base_url': 'https://api.openai.com/v1',  # Fallback to OpenAI
            'model': 'whisper-1',
            'provider': 'openai-whisper'
        }



async def text_to_speech_with_failover(
    message: str,
    voice: Optional[str] = None,
    model: Optional[str] = None,
    instructions: Optional[str] = None,
    audio_format: Optional[str] = None,
    initial_provider: Optional[str] = None
) -> Tuple[bool, Optional[dict], Optional[dict]]:
    """
    Text to speech with automatic failover to next available endpoint.
    
    Returns:
        Tuple of (success, tts_metrics, tts_config)
    """
    from voice_mcp.provider_discovery import provider_registry
    
    # Track which URLs we've tried
    tried_urls = set()
    last_error = None
    
    # If initial_provider specified, try it first
    if initial_provider:
        provider_urls = {'openai': 'https://api.openai.com/v1', 'kokoro': 'http://studio:8880/v1'}
        initial_url = provider_urls.get(initial_provider, initial_provider)
        if initial_url:
            tried_urls.add(initial_url)
            try:
                tts_config = await get_tts_config(initial_provider, voice, model, instructions)
                
                # Handle both new client object and legacy client_key
                if 'client' in tts_config:
                    openai_clients['_temp_tts'] = tts_config['client']
                    client_key = '_temp_tts'
                else:
                    client_key = tts_config.get('client_key', 'tts')
                
                success, tts_metrics = await text_to_speech(
                    text=message,
                    openai_clients=openai_clients,
                    tts_model=tts_config['model'],
                    tts_base_url=tts_config['base_url'],
                    tts_voice=tts_config['voice'],
                    debug=DEBUG,
                    debug_dir=DEBUG_DIR if DEBUG else None,
                    save_audio=SAVE_AUDIO,
                    audio_dir=AUDIO_DIR if SAVE_AUDIO else None,
                    client_key=client_key,
                    instructions=tts_config.get('instructions'),
                    audio_format=audio_format
                )
                
                # Clean up temporary client
                if '_temp_tts' in openai_clients:
                    del openai_clients['_temp_tts']
                
                if success:
                    return success, tts_metrics, tts_config
                
                # Mark endpoint as unhealthy
                await provider_registry.mark_unhealthy('tts', tts_config['base_url'], 'TTS request failed')
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Initial provider {initial_provider} failed: {e}")
    
    # Try remaining endpoints in order
    from voice_mcp.config import TTS_BASE_URLS
    
    for base_url in TTS_BASE_URLS:
        if base_url in tried_urls:
            continue
            
        tried_urls.add(base_url)
        
        try:
            # Try to get config for this specific base URL
            tts_config = await get_tts_config(None, voice, model, instructions)
            
            # Skip if we got a different URL than requested (means our preferred wasn't available)
            if tts_config.get('base_url') != base_url:
                continue
            
            # Handle both new client object and legacy client_key
            if 'client' in tts_config:
                openai_clients['_temp_tts'] = tts_config['client']
                client_key = '_temp_tts'
            else:
                client_key = tts_config.get('client_key', 'tts')
            
            success, tts_metrics = await text_to_speech(
                text=message,
                openai_clients=openai_clients,
                tts_model=tts_config['model'],
                tts_base_url=tts_config['base_url'],
                tts_voice=tts_config['voice'],
                debug=DEBUG,
                debug_dir=DEBUG_DIR if DEBUG else None,
                save_audio=SAVE_AUDIO,
                audio_dir=AUDIO_DIR if SAVE_AUDIO else None,
                client_key=client_key,
                instructions=tts_config.get('instructions'),
                audio_format=audio_format
            )
            
            # Clean up temporary client
            if '_temp_tts' in openai_clients:
                del openai_clients['_temp_tts']
            
            if success:
                logger.info(f"TTS succeeded with failover to: {base_url}")
                return success, tts_metrics, tts_config
            else:
                # Mark endpoint as unhealthy
                await provider_registry.mark_unhealthy('tts', base_url, 'TTS request failed')
                
        except Exception as e:
            last_error = str(e)
            logger.warning(f"TTS failed for {base_url}: {e}")
            # Mark endpoint as unhealthy
            await provider_registry.mark_unhealthy('tts', base_url, str(e))
    
    # All endpoints failed
    logger.error(f"All TTS endpoints failed. Last error: {last_error}")
    return False, None, None


async def speech_to_text(audio_data: np.ndarray, save_audio: bool = False, audio_dir: Optional[Path] = None) -> Optional[str]:
    """Convert audio to text"""
    logger.info(f"STT: Converting speech to text, audio data shape: {audio_data.shape}")
    
    # Get proper STT configuration using the new provider system
    stt_config = await get_stt_config()
    
    if DEBUG:
        logger.debug(f"STT config - Model: {stt_config['model']}, Base URL: {stt_config['base_url']}")
        logger.debug(f"Audio stats - Min: {audio_data.min()}, Max: {audio_data.max()}, Mean: {audio_data.mean():.2f}")
    
    wav_file = None
    export_file = None
    export_format = None
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file_obj:
            wav_file = wav_file_obj.name
            logger.debug(f"Writing audio to WAV file: {wav_file}")
            write(wav_file, SAMPLE_RATE, audio_data)
        
            # Save debug file for original recording
            if DEBUG:
                try:
                    with open(wav_file, 'rb') as f:
                        debug_path = save_debug_file(f.read(), "stt-input", "wav", DEBUG_DIR, DEBUG)
                        if debug_path:
                            logger.info(f"STT debug recording saved to: {debug_path}")
                except Exception as e:
                    logger.error(f"Failed to save debug WAV: {e}")
            
            # Save audio file if audio saving is enabled
            if save_audio and audio_dir:
                try:
                    with open(wav_file, 'rb') as f:
                        audio_path = save_debug_file(f.read(), "stt", "wav", audio_dir, True)
                        if audio_path:
                            logger.info(f"STT audio saved to: {audio_path}")
                except Exception as e:
                    logger.error(f"Failed to save audio WAV: {e}")
        
        try:
            # Import config for audio format
            from ..config import STT_AUDIO_FORMAT, validate_audio_format, get_format_export_params
            
            # Determine provider from base URL (simple heuristic)
            provider = "openai-whisper"
            # Check if using local Whisper endpoint
            if stt_config.get('base_url') and ("localhost" in stt_config['base_url'] or "127.0.0.1" in stt_config['base_url'] or "studio:2022" in stt_config['base_url']):
                    provider = "whisper-local"
            
            # Validate format for provider
            export_format = validate_audio_format(STT_AUDIO_FORMAT, provider, "stt")
            
            # Convert WAV to target format for upload
            logger.debug(f"Converting WAV to {export_format.upper()} for upload...")
            audio = AudioSegment.from_wav(wav_file)
            logger.debug(f"Audio loaded - Duration: {len(audio)}ms, Channels: {audio.channels}, Frame rate: {audio.frame_rate}")
            
            # Get export parameters for the format
            export_params = get_format_export_params(export_format)
            
            with tempfile.NamedTemporaryFile(suffix=f'.{export_format}', delete=False) as export_file_obj:
                export_file = export_file_obj.name
                audio.export(export_file, **export_params)
                upload_file = export_file
                logger.debug(f"{export_format.upper()} created for STT upload: {upload_file}")
            
            # Save debug file for upload version
            if DEBUG:
                try:
                    with open(upload_file, 'rb') as f:
                        debug_path = save_debug_file(f.read(), "stt-upload", export_format, DEBUG_DIR, DEBUG)
                        if debug_path:
                            logger.info(f"Upload audio saved to: {debug_path}")
                except Exception as e:
                    logger.error(f"Failed to save debug {export_format.upper()}: {e}")
            
            # Get file size for logging
            file_size = os.path.getsize(upload_file)
            logger.debug(f"Uploading {file_size} bytes to STT API...")
            
            with open(upload_file, 'rb') as audio_file:
                # Use the STT client from the configuration
                if 'client' in stt_config:
                    stt_client = stt_config['client']
                else:
                    # Fallback to legacy client
                    openai_clients['_temp_stt'] = openai_clients.get(stt_config.get('client_key', 'stt'))
                    stt_client = openai_clients['_temp_stt']
                
                transcription = await stt_client.audio.transcriptions.create(
                    model=stt_config['model'],
                    file=audio_file,
                    response_format="text"
                )
                
                logger.debug(f"STT API response type: {type(transcription)}")
                text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
                
                if text:
                    logger.info(f"✓ STT result: '{text}'")
                    return text
                else:
                    logger.warning("STT returned empty text")
                    return None
                        
        except Exception as e:
            logger.error(f"STT failed: {e}")
            logger.error(f"STT config when error occurred - Model: {stt_config.get('model', 'unknown')}, Base URL: {stt_config.get('base_url', 'unknown')}")
            if hasattr(e, 'response'):
                logger.error(f"HTTP status: {e.response.status_code if hasattr(e.response, 'status_code') else 'unknown'}")
                logger.error(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'unknown'}")
            return None
    finally:
        # Clean up temporary files
        if wav_file and os.path.exists(wav_file):
            try:
                os.unlink(wav_file)
                logger.debug(f"Cleaned up WAV file: {wav_file}")
            except Exception as e:
                logger.error(f"Failed to clean up WAV file: {e}")
        
        if 'export_file' in locals() and export_file and os.path.exists(export_file):
            try:
                os.unlink(export_file)
                logger.debug(f"Cleaned up {export_format.upper()} file: {export_file}")
            except Exception as e:
                logger.error(f"Failed to clean up {export_format.upper()} file: {e}")


async def play_audio_feedback(
    text: str, 
    openai_clients: dict, 
    enabled: Optional[bool] = None, 
    style: str = "whisper", 
    feedback_type: Optional[str] = None,
    voice: str = "nova",
    model: str = "gpt-4o-mini-tts"
) -> None:
    """Play an audio feedback chime
    
    Args:
        text: Which chime to play (either "listening" or "finished")
        openai_clients: OpenAI client instances (kept for compatibility, not used)
        enabled: Override global audio feedback setting
        style: Kept for compatibility, not used
        feedback_type: Kept for compatibility, not used
        voice: Kept for compatibility, not used
        model: Kept for compatibility, not used
    """
    # Use parameter override if provided, otherwise use global setting
    if enabled is False:
        return
    
    # If enabled is None, check global setting
    if enabled is None and not AUDIO_FEEDBACK_ENABLED:
        return
    
    try:
        # Play appropriate chime
        if text == "listening":
            await play_chime_start()
        elif text == "finished":
            await play_chime_end()
    except Exception as e:
        logger.debug(f"Audio feedback failed: {e}")
        # Don't interrupt the main flow if feedback fails


def record_audio(duration: float) -> np.ndarray:
    """Record audio from microphone"""
    logger.info(f"🎤 Recording audio for {duration}s...")
    if DEBUG:
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            logger.debug(f"Default input device: {default_input} - {devices[default_input]['name'] if default_input is not None else 'None'}")
            logger.debug(f"Recording config - Sample rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}, dtype: int16")
        except Exception as dev_e:
            logger.error(f"Error querying audio devices: {dev_e}")
    
    # Save current stdio state
    import sys
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        samples_to_record = int(duration * SAMPLE_RATE)
        logger.debug(f"Recording {samples_to_record} samples...")
        
        recording = sd.rec(
            samples_to_record,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.int16
        )
        sd.wait()
        
        flattened = recording.flatten()
        logger.info(f"✓ Recorded {len(flattened)} samples")
        
        if DEBUG:
            logger.debug(f"Recording stats - Min: {flattened.min()}, Max: {flattened.max()}, Mean: {flattened.mean():.2f}")
            # Check if recording contains actual audio (not silence)
            rms = np.sqrt(np.mean(flattened.astype(float) ** 2))
            logger.debug(f"RMS level: {rms:.2f} ({'likely silence' if rms < 100 else 'audio detected'})")
        
        return flattened
        
    except Exception as e:
        logger.error(f"Recording failed: {e}")
        logger.error(f"Audio config when error occurred - Sample rate: {SAMPLE_RATE}, Channels: {CHANNELS}")
        
        # Try to get more info about audio devices
        try:
            devices = sd.query_devices()
            logger.error(f"Available input devices:")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    logger.error(f"  {i}: {device['name']} (inputs: {device['max_input_channels']})")
        except Exception as dev_e:
            logger.error(f"Cannot query audio devices: {dev_e}")
        
        return np.array([])
    finally:
        # Restore stdio if it was changed
        if sys.stdin != original_stdin:
            sys.stdin = original_stdin
        if sys.stdout != original_stdout:
            sys.stdout = original_stdout
        if sys.stderr != original_stderr:
            sys.stderr = original_stderr


async def check_livekit_available() -> bool:
    """Check if LiveKit is available and has active rooms"""
    try:
        from livekit import api
        
        api_url = LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://")
        lk_api = api.LiveKitAPI(api_url, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        
        rooms = await lk_api.room.list_rooms(api.ListRoomsRequest())
        active_rooms = [r for r in rooms.rooms if r.num_participants > 0]
        
        return len(active_rooms) > 0
        
    except Exception as e:
        logger.debug(f"LiveKit not available: {e}")
        return False


async def livekit_ask_voice_question(question: str, room_name: str = "", timeout: float = 60.0) -> str:
    """Ask voice question using LiveKit transport"""
    try:
        from livekit import rtc, api
        from livekit.agents import Agent, AgentSession
        from livekit.plugins import openai as lk_openai, silero
        
        # Auto-discover room if needed
        if not room_name:
            api_url = LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://")
            lk_api = api.LiveKitAPI(api_url, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            
            rooms = await lk_api.room.list_rooms(api.ListRoomsRequest())
            for room in rooms.rooms:
                if room.num_participants > 0:
                    room_name = room.name
                    break
            
            if not room_name:
                return "No active LiveKit rooms found"
        
        # Setup TTS and STT for LiveKit
        # Get default providers from registry
        tts_config = await get_tts_config()
        stt_config = await get_stt_config()
        tts_client = lk_openai.TTS(voice=tts_config['voice'], base_url=tts_config['base_url'], model=tts_config['model'])
        stt_client = lk_openai.STT(base_url=stt_config['base_url'], model=stt_config['model'])
        
        # Create simple agent that speaks and listens
        class VoiceAgent(Agent):
            def __init__(self):
                super().__init__(
                    instructions="Speak the message and listen for response",
                    stt=stt_client,
                    tts=tts_client,
                    llm=None
                )
                self.response = None
                self.has_spoken = False
            
            async def on_enter(self):
                await asyncio.sleep(0.5)
                if self.session:
                    await self.session.say(question, allow_interruptions=True)
                    self.has_spoken = True
            
            async def on_user_turn_completed(self, chat_ctx, new_message):
                if self.has_spoken and not self.response and new_message.content:
                    self.response = new_message.content[0]
        
        # Connect and run
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity("voice-mcp-bot").with_name("Voice MCP Bot")
        token.with_grants(api.VideoGrants(
            room_join=True, room=room_name,
            can_publish=True, can_subscribe=True,
        ))
        
        room = rtc.Room()
        await room.connect(LIVEKIT_URL, token.to_jwt())
        
        if not room.remote_participants:
            await room.disconnect()
            return "No participants in LiveKit room"
        
        agent = VoiceAgent()
        vad = silero.VAD.load()
        session = AgentSession(vad=vad)
        await session.start(room=room, agent=agent)
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if agent.response:
                await room.disconnect()
                return agent.response
            await asyncio.sleep(0.1)
        
        await room.disconnect()
        return f"No response within {timeout}s"
        
    except Exception as e:
        logger.error(f"LiveKit error: {e}")
        return f"LiveKit error: {str(e)}"


@mcp.tool()
async def converse(
    message: str,
    wait_for_response: bool = True,
    listen_duration: float = 15.0,
    transport: Literal["auto", "local", "livekit"] = "auto",
    room_name: str = "",
    timeout: float = 60.0,
    voice: Optional[str] = None,
    tts_provider: Optional[Literal["openai", "kokoro"]] = None,
    tts_model: Optional[str] = None,
    tts_instructions: Optional[str] = None,
    audio_feedback: Optional[bool] = None,
    audio_feedback_style: Optional[str] = None,
    audio_format: Optional[str] = None
) -> str:
    """Have a voice conversation - speak a message and optionally listen for response.
    
    PRIVACY NOTICE: When wait_for_response is True, this tool will access your microphone
    to record audio for speech-to-text conversion. Audio is processed using the configured
    STT service and is not permanently stored. Do not use upper case except for acronyms as the TTS will spell these out.
    
    Args:
        message: The message to speak
        wait_for_response: Whether to listen for a response after speaking (default: True)
        listen_duration: How long to listen for response in seconds (default: 15.0)
        transport: Transport method - "auto" (try LiveKit then local), "local" (direct mic), "livekit" (room-based)
        room_name: LiveKit room name (only for livekit transport, auto-discovered if empty)
        timeout: Maximum wait time for response in seconds (LiveKit only)
        voice: Override TTS voice - ONLY specify if user explicitly requests a specific voice
               The system automatically selects the best available voice based on preferences.
               Examples: nova, shimmer (OpenAI); af_sky, af_sarah, am_adam (Kokoro)
               IMPORTANT: Never use 'coral' voice.
        tts_provider: TTS provider - ONLY specify if user explicitly requests or for failover testing
                      The system automatically selects based on availability and preferences.
        tts_model: TTS model - ONLY specify for specific features (e.g., gpt-4o-mini-tts for emotions)
                   The system automatically selects the best available model.
                   Options: tts-1, tts-1-hd, gpt-4o-mini-tts (OpenAI); Kokoro uses tts-1
        tts_instructions: Tone/style instructions for gpt-4o-mini-tts model only (e.g., "Speak in a cheerful tone", "Sound angry", "Be extremely sad")
        audio_feedback: Override global audio feedback setting (default: None uses VOICE_MCP_AUDIO_FEEDBACK env var)
        audio_feedback_style: Audio feedback style - "whisper" (default) or "shout" (default: None uses VOICE_MCP_FEEDBACK_STYLE env var)
        audio_format: Override audio format (pcm, mp3, wav, flac, aac, opus) - defaults to VOICEMODE_TTS_AUDIO_FORMAT env var
        If wait_for_response is False: Confirmation that message was spoken
        If wait_for_response is True: The voice response received (or error/timeout message)
    
    Examples:
        - Ask a question: converse("What's your name?")  # Let system auto-select voice/model
        - Make a statement and wait: converse("Tell me more about that")  # Auto-selection recommended
        - Just speak without waiting: converse("Goodbye!", wait_for_response=False)
        - User requests specific voice: converse("Hello", voice="nova")  # Only when explicitly requested
        - Need HD quality: converse("High quality speech", tts_model="tts-1-hd")  # Only for specific features
        
    Emotional Speech (Requires OpenAI API):
        - Excitement: converse("We did it!", tts_model="gpt-4o-mini-tts", tts_instructions="Sound extremely excited and celebratory")
        - Sadness: converse("I'm sorry for your loss", tts_model="gpt-4o-mini-tts", tts_instructions="Sound gentle and sympathetic")
        - Urgency: converse("Watch out!", tts_model="gpt-4o-mini-tts", tts_instructions="Sound urgent and concerned")
        - Humor: converse("That's hilarious!", tts_model="gpt-4o-mini-tts", tts_instructions="Sound amused and playful")
        
    Note: Emotional speech uses OpenAI's gpt-4o-mini-tts model and incurs API costs (~$0.02/minute)
    """
    logger.info(f"Converse: '{message[:50]}{'...' if len(message) > 50 else ''}' (wait_for_response: {wait_for_response})")
    
    # Run startup initialization if needed
    await startup_initialization()
    
    # Get event logger and start session
    event_logger = get_event_logger()
    session_id = None
    
    # Check time since last session for AI thinking time
    global last_session_end_time
    current_time = time.time()
    
    if last_session_end_time and wait_for_response:
        time_since_last = current_time - last_session_end_time
        logger.info(f"Time since last session: {time_since_last:.1f}s (AI thinking time)")
    
    # For conversations with responses, create a session
    if event_logger and wait_for_response:
        session_id = event_logger.start_session()
        # Log the time since last session as an event
        if last_session_end_time:
            event_logger.log_event("TIME_SINCE_LAST_SESSION", {
                "seconds": time_since_last
            })
    
    # Log tool request start (after session is created)
    if event_logger:
        # If we have a session, the event will be associated with it
        log_tool_request_start("converse", {
            "wait_for_response": wait_for_response,
            "listen_duration": listen_duration if wait_for_response else None
        })
    
    # Track execution time and resources
    start_time = time.time()
    if DEBUG:
        import resource
        start_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.debug(f"Starting converse - Memory: {start_memory} KB")
    
    result = None
    success = False
    
    try:
        # If not waiting for response, just speak and return
        if not wait_for_response:
            try:
                async with audio_operation_lock:
                    success, tts_metrics, tts_config = await text_to_speech_with_failover(
                        message=message,
                        voice=voice,
                        model=tts_model,
                        instructions=tts_instructions,
                        audio_format=audio_format,
                        initial_provider=tts_provider
                    )
                    
                # Include timing info if available
                timing_info = ""
                timing_str = ""
                if success and tts_metrics:
                    timing_info = f" (gen: {tts_metrics.get('generation', 0):.1f}s, play: {tts_metrics.get('playback', 0):.1f}s)"
                    # Create timing string for statistics
                    timing_parts = []
                    if 'ttfa' in tts_metrics:
                        timing_parts.append(f"ttfa {tts_metrics['ttfa']:.1f}s")
                    if 'generation' in tts_metrics:
                        timing_parts.append(f"tts_gen {tts_metrics['generation']:.1f}s")
                    if 'playback' in tts_metrics:
                        timing_parts.append(f"tts_play {tts_metrics['playback']:.1f}s")
                    timing_str = ", ".join(timing_parts)
                
                result = f"✓ Message spoken successfully{timing_info}" if success else "✗ Failed to speak message"
                
                # Track statistics for speak-only interaction
                track_voice_interaction(
                    message=message,
                    response="[speak-only]",
                    timing_str=timing_str if success else None,
                    transport="speak-only",
                    voice_provider=tts_provider,
                    voice_name=voice,
                    model=tts_model,
                    success=success,
                    error_message=None if success else "TTS failed"
                )
                
                logger.info(f"Speak-only result: {result}")
                # success is already set correctly from TTS result
                return result
            except Exception as e:
                logger.error(f"Speak error: {e}")
                error_msg = f"Error: {str(e)}"
                
                # Track failed speak-only interaction
                track_voice_interaction(
                    message=message,
                    response="[error]",
                    timing_str=None,
                    transport="speak-only",
                    voice_provider=tts_provider,
                    voice_name=voice,
                    model=tts_model,
                    success=False,
                    error_message=str(e)
                )
                
                logger.error(f"Returning error: {error_msg}")
                result = error_msg
                return result
        
        # Otherwise, speak and then listen for response
        # Determine transport method
        if transport == "auto":
            if await check_livekit_available():
                transport = "livekit"
                logger.info("Auto-selected LiveKit transport")
            else:
                transport = "local"
                logger.info("Auto-selected local transport")
        
        if transport == "livekit":
            # For LiveKit, use the existing function but with the message parameter
            livekit_result = await livekit_ask_voice_question(message, room_name, timeout)
            
            # Track LiveKit interaction (simplified since we don't have detailed timing)
            success = not livekit_result.startswith("Error:") and not livekit_result.startswith("No ")
            track_voice_interaction(
                message=message,
                response=livekit_result,
                timing_str=None,  # LiveKit doesn't provide detailed timing
                transport="livekit",
                voice_provider="livekit",  # LiveKit manages its own providers
                voice_name=voice,
                model=tts_model,
                success=success,
                error_message=livekit_result if not success else None
            )
            
            result = livekit_result
            success = not livekit_result.startswith("Error:") and not livekit_result.startswith("No ")
            return result
        
        elif transport == "local":
            # Local microphone approach with timing
            timings = {}
            try:
                async with audio_operation_lock:
                    # Speak the message
                    tts_start = time.perf_counter()
                    tts_success, tts_metrics, tts_config = await text_to_speech_with_failover(
                        message=message,
                        voice=voice,
                        model=tts_model,
                        instructions=tts_instructions,
                        audio_format=audio_format,
                        initial_provider=tts_provider
                    )
                    
                    # Add TTS sub-metrics
                    if tts_metrics:
                        timings['ttfa'] = tts_metrics.get('ttfa', 0)
                        timings['tts_gen'] = tts_metrics.get('generation', 0)
                        timings['tts_play'] = tts_metrics.get('playback', 0)
                    timings['tts_total'] = time.perf_counter() - tts_start
                    
                    if not tts_success:
                        result = "Error: Could not speak message"
                        return result
                    
                    # Brief pause before listening
                    await asyncio.sleep(0.5)
                    
                    # Play "listening" feedback sound
                    await play_audio_feedback("listening", openai_clients, audio_feedback, audio_feedback_style or "whisper")
                    
                    # Record response
                    logger.info(f"🎤 Listening for {listen_duration} seconds...")
                    
                    # Log recording start
                    if event_logger:
                        event_logger.log_event(event_logger.RECORDING_START)
                    
                    record_start = time.perf_counter()
                    audio_data = await asyncio.get_event_loop().run_in_executor(
                        None, record_audio, listen_duration
                    )
                    timings['record'] = time.perf_counter() - record_start
                    
                    # Log recording end
                    if event_logger:
                        event_logger.log_event(event_logger.RECORDING_END, {
                            "duration": timings['record'],
                            "samples": len(audio_data)
                        })
                    
                    # Play "finished" feedback sound
                    await play_audio_feedback("finished", openai_clients, audio_feedback, audio_feedback_style or "whisper")
                    
                    # Mark the end of recording - this is when user expects response to start
                    user_done_time = time.perf_counter()
                    logger.info(f"Recording finished at {user_done_time - tts_start:.1f}s from start")
                    
                    if len(audio_data) == 0:
                        result = "Error: Could not record audio"
                        return result
                    
                    # Convert to text
                    # Log STT start
                    if event_logger:
                        event_logger.log_event(event_logger.STT_START)
                    
                    stt_start = time.perf_counter()
                    response_text = await speech_to_text(audio_data, SAVE_AUDIO, AUDIO_DIR if SAVE_AUDIO else None)
                    timings['stt'] = time.perf_counter() - stt_start
                    
                    # Log STT complete
                    if event_logger:
                        if response_text:
                            event_logger.log_event(event_logger.STT_COMPLETE, {"text": response_text})
                        else:
                            event_logger.log_event(event_logger.STT_NO_SPEECH)
                
                # Calculate total time (use tts_total instead of sub-metrics)
                main_timings = {k: v for k, v in timings.items() if k in ['tts_total', 'record', 'stt']}
                total_time = sum(main_timings.values())
                
                # Format timing string
                timing_parts = []
                
                # Detailed breakdown
                if 'ttfa' in timings:
                    timing_parts.append(f"ttfa {timings['ttfa']:.1f}s")
                if 'tts_gen' in timings:
                    timing_parts.append(f"tts_gen {timings['tts_gen']:.1f}s")
                if 'tts_play' in timings:
                    timing_parts.append(f"tts_play {timings['tts_play']:.1f}s")
                if 'tts_total' in timings:
                    timing_parts.append(f"tts_total {timings['tts_total']:.1f}s")
                if 'record' in timings:
                    timing_parts.append(f"record {timings['record']:.1f}s")
                if 'stt' in timings:
                    timing_parts.append(f"stt {timings['stt']:.1f}s")
                
                timing_str = ", ".join(timing_parts)
                timing_str += f", total {total_time:.1f}s"
                
                # Track statistics for full conversation interaction
                actual_response = response_text or "[no speech detected]"
                track_voice_interaction(
                    message=message,
                    response=actual_response,
                    timing_str=timing_str,
                    transport=transport,
                    voice_provider=tts_provider,
                    voice_name=voice,
                    model=tts_model,
                    success=bool(response_text),  # Success if we got a response
                    error_message=None if response_text else "No speech detected"
                )
                
                # End event logging session
                if event_logger and session_id:
                    event_logger.end_session()
                
                if response_text:
                    result = f"Voice response: {response_text} | Timing: {timing_str}"
                    success = True
                else:
                    result = f"No speech detected | Timing: {timing_str}"
                    success = True  # Not an error, just no speech
                return result
                    
            except Exception as e:
                logger.error(f"Local voice error: {e}")
                if DEBUG:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Track failed conversation interaction
                track_voice_interaction(
                    message=message,
                    response="[error]",
                    timing_str=None,
                    transport=transport,
                    voice_provider=tts_provider,
                    voice_name=voice,
                    model=tts_model,
                    success=False,
                    error_message=str(e)
                )
                
                result = f"Error: {str(e)}"
                return result
            
        else:
            result = f"Unknown transport: {transport}"
            return result
            
    except Exception as e:
        logger.error(f"Unexpected error in converse: {e}")
        if DEBUG:
            logger.error(f"Full traceback: {traceback.format_exc()}")
        result = f"Unexpected error: {str(e)}"
        return result
        
    finally:
        # Log tool request end
        if event_logger:
            log_tool_request_end("converse", success=success)
        
        # Update last session end time for tracking AI thinking time
        if wait_for_response:
            last_session_end_time = time.time()
        
        # Log execution metrics
        elapsed = time.time() - start_time
        logger.info(f"Converse completed in {elapsed:.2f}s")
        
        if DEBUG:
            import resource
            import gc
            end_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            memory_delta = end_memory - start_memory
            logger.debug(f"Memory delta: {memory_delta} KB (start: {start_memory}, end: {end_memory})")
            
            # Force garbage collection
            collected = gc.collect()
            logger.debug(f"Garbage collected {collected} objects")


@mcp.tool()
async def ask_voice_question(
    question: str,
    duration: float = 15.0,
    voice: Optional[str] = None,
    tts_provider: Optional[Literal["openai", "kokoro"]] = None,
    tts_model: Optional[str] = None,
    tts_instructions: Optional[str] = None,
    audio_format: Optional[str] = None
) -> str:
    """Ask a voice question and listen for the answer.
    
    PRIVACY NOTICE: This tool will access your microphone to record audio
    for speech-to-text conversion. Audio is processed using the configured
    STT service and is not permanently stored.
    
    Args:
        question: The question to ask
        duration: How long to listen for response in seconds (default: 15.0)
        voice: Override TTS voice - ONLY specify if user explicitly requests
        tts_provider: TTS provider - ONLY specify if user explicitly requests
        tts_model: TTS model - ONLY specify for specific features
        tts_instructions: Tone/style instructions for gpt-4o-mini-tts model only
        audio_format: Override audio format (opus, mp3, wav, flac, aac, pcm)
    
    Returns:
        The voice response received
    
    This is a convenience wrapper around converse() for backward compatibility.
    """
    return await converse(
        message=question,
        wait_for_response=True,
        listen_duration=duration,
        voice=voice,
        tts_provider=tts_provider,
        tts_model=tts_model,
        tts_instructions=tts_instructions,
        audio_format=audio_format
    )


@mcp.tool()
async def voice_registry() -> str:
    """Get the current voice provider registry showing all discovered endpoints.
    
    Returns a formatted view of all TTS and STT endpoints with their:
    - Health status
    - Available models
    - Available voices (TTS only)
    - Response times
    - Last health check time
    
    This allows the LLM to see what voice services are currently available.
    """
    # Ensure registry is initialized
    await provider_registry.initialize()
    
    # Get registry data
    registry_data = provider_registry.get_registry_for_llm()
    
    # Format the output
    lines = ["Voice Provider Registry", "=" * 50, ""]
    
    # TTS Endpoints
    lines.append("TTS Endpoints:")
    lines.append("-" * 30)
    
    for url, info in registry_data["tts"].items():
        status = "✅" if info["healthy"] else "❌"
        lines.append(f"\n{status} {url}")
        
        if info["healthy"]:
            lines.append(f"   Models: {', '.join(info['models']) if info['models'] else 'none detected'}")
            lines.append(f"   Voices: {', '.join(info['voices']) if info['voices'] else 'none detected'}")
            if info["response_time_ms"]:
                lines.append(f"   Response Time: {info['response_time_ms']:.0f}ms")
        else:
            if info.get("error"):
                lines.append(f"   Error: {info['error']}")
        
        lines.append(f"   Last Check: {info['last_check']}")
    
    # STT Endpoints
    lines.append("\n\nSTT Endpoints:")
    lines.append("-" * 30)
    
    for url, info in registry_data["stt"].items():
        status = "✅" if info["healthy"] else "❌"
        lines.append(f"\n{status} {url}")
        
        if info["healthy"]:
            lines.append(f"   Models: {', '.join(info['models']) if info['models'] else 'none detected'}")
            if info["response_time_ms"]:
                lines.append(f"   Response Time: {info['response_time_ms']:.0f}ms")
        else:
            if info.get("error"):
                lines.append(f"   Error: {info['error']}")
        
        lines.append(f"   Last Check: {info['last_check']}")
    
    return "\n".join(lines)


async def voice_chat(
    initial_message: Optional[str] = None,
    max_turns: int = 10,
    listen_duration: float = 15.0,
    voice: Optional[str] = None,
    tts_provider: Optional[Literal["openai", "kokoro"]] = None
) -> str:
    """Start an interactive voice chat session.
    
    PRIVACY NOTICE: This tool will access your microphone for the duration
    of the chat session. Say "goodbye", "exit", or "end chat" to stop.
    
    Args:
        initial_message: Optional greeting to start the conversation
        max_turns: Maximum number of conversation turns (default: 10)
        listen_duration: How long to listen each turn in seconds (default: 15.0)
        voice: Override TTS voice
        tts_provider: TTS provider to use - "openai" or "kokoro"
    
    Returns:
        Summary of the conversation
    
    Note: This is a simplified version. The full voice-chat command provides
    a more interactive experience with the LLM handling the conversation flow.
    """
    transcript = []
    
    # Start with initial message if provided
    if initial_message:
        result = await converse(
            message=initial_message,
            wait_for_response=True,
            listen_duration=listen_duration,
            voice=voice,
            tts_provider=tts_provider
        )
        transcript.append(f"Assistant: {initial_message}")
        if "Voice response:" in result:
            user_response = result.split("Voice response:")[1].split("|")[0].strip()
            transcript.append(f"User: {user_response}")
            
            # Check for exit phrases
            exit_phrases = ["goodbye", "exit", "end chat", "stop", "quit"]
            if any(phrase in user_response.lower() for phrase in exit_phrases):
                return "\n".join(transcript) + "\n\nChat ended by user."
    
    # Continue conversation for remaining turns
    turns_remaining = max_turns - (1 if initial_message else 0)
    
    return f"Voice chat started. Use the converse tool in a loop to continue the conversation.\n\nTranscript so far:\n" + "\n".join(transcript)
