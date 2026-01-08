import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
import queue
from datetime import datetime
from models.voxtral import classify_query
from models.ollama import get_response_from_ollama

# ========== Global Thread-Safe Variables ==========
# These are used instead of session state in threads to avoid ScriptRunContext issues
global_audio_queue = queue.Queue()
global_recording_flag = threading.Event()
global_stop_speech_flag = threading.Event()
global_speech_paused_flag = threading.Event()
global_lock = threading.Lock()

# ========== Page Configuration ==========
st.set_page_config(
    page_title="🎧 Agentic  Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Custom CSS ==========
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9ff;
    }
    .recording-status {
        background: linear-gradient(90deg, #ff6b6b, #feca57);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }
    .assistant-bubble {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .controls-container {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
    }
    .voice-wave {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3px;
        margin: 10px 0;
    }
    .wave-bar {
        width: 4px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        animation: wave 1.5s ease-in-out infinite;
        border-radius: 2px;
    }
    .wave-bar:nth-child(1) { height: 20px; animation-delay: 0s; }
    .wave-bar:nth-child(2) { height: 30px; animation-delay: 0.1s; }
    .wave-bar:nth-child(3) { height: 25px; animation-delay: 0.2s; }
    .wave-bar:nth-child(4) { height: 35px; animation-delay: 0.3s; }
    .wave-bar:nth-child(5) { height: 20px; animation-delay: 0.4s; }
    @keyframes wave {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(0.3); }
    }
</style>
""", unsafe_allow_html=True)

# ========== TTS Setup ==========
@st.cache_resource
def init_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 0.9)
        voices = engine.getProperty('voices')
        if voices and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        return engine
    except Exception as e:
        st.error(f"TTS initialization error: {e}")
        return None

engine = init_tts()

# ========== Session State Initialization ==========
def init_session_state():
    default_states = {
        'recording': False,
        'transcript': "",
        'is_speaking': False,
        'speech_paused': False,
        'conversation_history': [],
        'processing': False,
        'voice_settings': {'rate': 165, 'volume': 0.9, 'voice_index': 1},
        'current_audio_text': "",
        'microphone_available': True,
        'last_speech_time': 0,
        'recording_thread': None,
        'speech_thread': None
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ========== Thread-Safe Helper Functions ==========
def safe_put_message(message):
    """Thread-safe way to add messages to queue"""
    try:
        global_audio_queue.put(message, timeout=1)
    except queue.Full:
        pass  # Ignore if queue is full

def sync_global_flags():
    """Sync global flags with session state"""
    with global_lock:
        if st.session_state.recording:
            global_recording_flag.set()
        else:
            global_recording_flag.clear()
            
        if getattr(st.session_state, 'stop_speech_flag', False):
            global_stop_speech_flag.set()
        else:
            global_stop_speech_flag.clear()
            
        if st.session_state.speech_paused:
            global_speech_paused_flag.set()
        else:
            global_speech_paused_flag.clear()

# ========== Voice Functions ==========
def check_microphone():
    """Check if microphone is available"""
    try:
        with sr.Microphone() as source:
            pass
        return True
    except Exception as e:
        st.error(f"Microphone not available: {e}")
        return False

def speak_text(text):
    """Improved TTS with better control"""
    def speak():
        try:
            if not engine:
                return
                
            # Update session state in main thread context
            st.session_state.is_speaking = True
            st.session_state.speech_paused = False
            st.session_state.current_audio_text = text
            global_stop_speech_flag.clear()
            global_speech_paused_flag.clear()
            
            # Split text into sentences for better control
            sentences = text.replace('!', '.').replace('?', '.').split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for i, sentence in enumerate(sentences):
                if global_stop_speech_flag.is_set():
                    break
                    
                # Check for pause
                while global_speech_paused_flag.is_set() and not global_stop_speech_flag.is_set():
                    time.sleep(0.1)
                
                if not global_stop_speech_flag.is_set():
                    engine.say(sentence)
                    engine.runAndWait()
                    
        except Exception as e:
            safe_put_message(f"ERROR:TTS Error: {e}")
        finally:
            # Update session state
            st.session_state.is_speaking = False
            st.session_state.speech_paused = False
            st.session_state.current_audio_text = ""
            st.session_state.last_speech_time = time.time()
            global_stop_speech_flag.clear()
            global_speech_paused_flag.clear()
    
    if not st.session_state.is_speaking and engine:
        st.session_state.speech_thread = threading.Thread(target=speak, daemon=True)
        st.session_state.speech_thread.start()

def stop_speaking():
    """Stop current speech"""
    try:
        global_stop_speech_flag.set()
        st.session_state.speech_paused = False
        if engine:
            engine.stop()
        st.session_state.is_speaking = False
        st.session_state.current_audio_text = ""
    except Exception as e:
        st.error(f"Error stopping speech: {e}")

def pause_resume_speech():
    """Toggle pause/resume for speech"""
    if st.session_state.is_speaking:
        st.session_state.speech_paused = not st.session_state.speech_paused
        if st.session_state.speech_paused:
            global_speech_paused_flag.set()
        else:
            global_speech_paused_flag.clear()

def listen_continuously():
    """Improved continuous listening with thread-safe operations"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    
    try:
        with sr.Microphone() as source:
            safe_put_message("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            safe_put_message("✅ Microphone ready, listening...")
            
            accumulated_text = ""
            silence_count = 0
            
            while global_recording_flag.is_set():
                try:
                    # Listen for audio with shorter timeout
                    audio = recognizer.listen(source, phrase_time_limit=3, timeout=0.5)
                    
                    # Recognize speech
                    text = recognizer.recognize_google(audio, language='en-US')
                    
                    if text.strip():
                        accumulated_text += text + " "
                        silence_count = 0
                        # Update transcript in real-time
                        safe_put_message(f"TRANSCRIPT:{accumulated_text.strip()}")
                    
                except sr.WaitTimeoutError:
                    silence_count += 1
                    # If too much silence, finalize the transcript
                    if silence_count > 8 and accumulated_text:
                        safe_put_message(f"FINAL:{accumulated_text.strip()}")
                        accumulated_text = ""
                        silence_count = 0
                    continue
                    
                except sr.UnknownValueError:
                    # Could not understand audio
                    silence_count += 1
                    continue
                    
                except sr.RequestError as e:
                    safe_put_message(f"ERROR:Speech recognition error: {e}")
                    break
                    
                except Exception as e:
                    safe_put_message(f"ERROR:Unexpected error: {e}")
                    break
            
            # Finalize any remaining text
            if accumulated_text:
                safe_put_message(f"FINAL:{accumulated_text.strip()}")
                
    except Exception as e:
        safe_put_message(f"ERROR:Microphone error: {e}")

def start_recording():
    """Start voice recording"""
    if not check_microphone():
        st.session_state.microphone_available = False
        return
    
    st.session_state.recording = True
    st.session_state.transcript = ""
    st.session_state.microphone_available = True
    
    # Clear the global queue
    while not global_audio_queue.empty():
        try:
            global_audio_queue.get_nowait()
        except queue.Empty:
            break
    
    # Sync flags and start recording thread
    sync_global_flags()
    st.session_state.recording_thread = threading.Thread(target=listen_continuously, daemon=True)
    st.session_state.recording_thread.start()

def stop_recording():
    """Stop voice recording"""
    st.session_state.recording = False
    sync_global_flags()

# ========== UI Layout ==========
st.markdown('<h1 class="main-header">🎧 Agentic Assistant</h1>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Voice Settings
    st.subheader("🔊 Voice Settings")
    rate = st.slider("Speech Rate", 100, 300, st.session_state.voice_settings['rate'])
    volume = st.slider("Volume", 0.0, 1.0, st.session_state.voice_settings['volume'])
    
    # Update voice settings
    if rate != st.session_state.voice_settings['rate'] or volume != st.session_state.voice_settings['volume']:
        st.session_state.voice_settings['rate'] = rate
        st.session_state.voice_settings['volume'] = volume
        if engine:
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
    
    st.subheader("🎙️ Recording Settings")
    auto_send = st.checkbox("Auto-send after recording", value=True)
    show_live_transcript = st.checkbox("Show live transcript", value=True)
    
    # Microphone test
    if st.button("🎤 Test Microphone"):
        if check_microphone():
            st.success("✅ Microphone working!")
        else:
            st.error("❌ Microphone not available")
    
    st.subheader("💬 Conversation")
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.rerun()
    
    if st.button("💾 Export Chat"):
        chat_export = "\n".join([
            f"[{msg['timestamp']}] {msg['type'].upper()}: {msg['content']}"
            for msg in st.session_state.conversation_history
        ])
        st.download_button(
            "Download Chat History",
            chat_export,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Sync global flags before UI updates
sync_global_flags()

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    # Recording Controls
    st.markdown('<div class="controls-container">', unsafe_allow_html=True)
    st.subheader("🎙️ Voice Controls")
    
    control_col1, control_col2, control_col3, control_col4 = st.columns(4)
    
    with control_col1:
        if not st.session_state.recording:
            if st.button("🎙️ Start Recording", type="primary", use_container_width=True):
                start_recording()
        else:
            if st.button("🛑 Stop Recording", type="secondary", use_container_width=True):
                stop_recording()
    
    with control_col2:
        if st.session_state.is_speaking:
            if st.button("🔇 Stop Speaking", use_container_width=True):
                stop_speaking()
        else:
            st.button("🔇 Stop Speaking", disabled=True, use_container_width=True)
    
    with control_col3:
        if st.session_state.is_speaking:
            pause_text = "▶️ Resume" if st.session_state.speech_paused else "⏸️ Pause"
            if st.button(pause_text, use_container_width=True):
                pause_resume_speech()
        else:
            st.button("⏸️ Pause", disabled=True, use_container_width=True)
    
    with control_col4:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Status Panel
    st.subheader("📊 Status")
    
    if st.session_state.recording:
        st.markdown('<div class="recording-status">🔴 Recording Active</div>', unsafe_allow_html=True)
        # Show voice wave animation
        st.markdown("""
        <div class="voice-wave">
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Ready")
    
    if st.session_state.is_speaking:
        if st.session_state.speech_paused:
            st.warning("⏸️ Speech Paused")
        else:
            st.info("📢 Speaking...")
    
    if st.session_state.processing:
        st.info("🤔 Processing...")
    
    if not st.session_state.microphone_available:
        st.error("❌ Microphone unavailable")

# Process audio queue and update transcript
if st.session_state.recording or not global_audio_queue.empty():
    messages_processed = 0
    while not global_audio_queue.empty() and messages_processed < 5:
        try:
            message = global_audio_queue.get_nowait()
            messages_processed += 1
            
            if message.startswith("TRANSCRIPT:"):
                text = message.replace("TRANSCRIPT:", "")
                st.session_state.transcript = text
            elif message.startswith("FINAL:"):
                text = message.replace("FINAL:", "")
                st.session_state.transcript = text
                if not st.session_state.recording:  # Auto-finalize
                    break
            elif message.startswith("ERROR:"):
                error_msg = message.replace("ERROR:", "")
                st.error(error_msg)
                st.session_state.recording = False
                sync_global_flags()
            else:
                # Status messages
                st.info(message)
                
        except queue.Empty:
            break

# Show current transcript
if st.session_state.transcript and show_live_transcript:
    st.info(f"🎤 Transcript: {st.session_state.transcript}")

# Process recorded query
if st.session_state.transcript and not st.session_state.recording:
    query = st.session_state.transcript
    
    col_query, col_send, col_clear = st.columns([3, 1, 1])
    with col_query:
        edited_query = st.text_input("📝 Edit your query:", value=query, key=f"edit_query_{time.time()}")
    with col_send:
        st.write("")  # spacing
        send_query = st.button("📤 Send", type="primary")
    with col_clear:
        st.write("")  # spacing
        if st.button("🗑️ Clear"):
            st.session_state.transcript = ""
            st.rerun()
    
    if send_query or (auto_send and query and time.time() - st.session_state.last_speech_time > 1):
        final_query = edited_query if edited_query else query
        
        if final_query.strip():
            st.session_state.processing = True
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                'type': 'user',
                'content': final_query,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Process query
            try:
                with st.spinner("Processing your request..."):
                    intent = classify_query(final_query)
                    response = get_response_from_ollama(final_query, intent)
                
                # Add response to history
                st.session_state.conversation_history.append({
                    'type': 'assistant',
                    'content': response,
                    'intent': intent,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
                # Speak response
                speak_text(response)
                
            except Exception as e:
                error_msg = f"Error processing query: {e}"
                st.error(error_msg)
                st.session_state.conversation_history.append({
                    'type': 'assistant',
                    'content': error_msg,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            
            finally:
                st.session_state.processing = False
                st.session_state.transcript = ""
                st.rerun()

# Manual text input
st.markdown("---")
st.subheader("💬 Manual Input")
manual_col1, manual_col2 = st.columns([4, 1])

with manual_col1:
    manual_query = st.text_input("Type your message:", placeholder="Ask me anything...")

with manual_col2:
    st.write("")  # spacing
    manual_send = st.button("📤 Send Message", type="primary")

if manual_send and manual_query.strip():
    # Add to conversation history
    st.session_state.conversation_history.append({
        'type': 'user',
        'content': manual_query,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })
    
    try:
        with st.spinner("Processing..."):
            intent = classify_query(manual_query)
            response = get_response_from_ollama(manual_query, intent)
        
        # Add response to history
        st.session_state.conversation_history.append({
            'type': 'assistant',
            'content': response,
            'intent': intent,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # Speak response
        speak_text(response)
        
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.rerun()

# Show current speech status
if st.session_state.is_speaking and st.session_state.current_audio_text:
    st.info(f"🔊 Currently speaking: {st.session_state.current_audio_text[:100]}...")

# Conversation History
if st.session_state.conversation_history:
    st.markdown("---")
    st.subheader("💬 Conversation History")
    
    # Display conversation in reverse order (newest first)
    for i, msg in enumerate(reversed(st.session_state.conversation_history[-10:])):  # Show last 10 messages
        if msg['type'] == 'user':
            st.markdown(f"""
            <div class="chat-bubble user-bubble">
                <strong>You</strong> <small>({msg['timestamp']})</small><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            intent_info = f" | Intent: {msg.get('intent', 'N/A')}" if 'intent' in msg else ""
            st.markdown(f"""
            <div class="chat-bubble assistant-bubble">
                <strong>Assistant</strong> <small>({msg['timestamp']}{intent_info})</small><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Option to replay audio
            replay_col1, replay_col2 = st.columns([1, 4])
            with replay_col1:
                if st.button(f"🔊", key=f"replay_{len(st.session_state.conversation_history)-i}", 
                           help="Replay this message"):
                    speak_text(msg['content'])

# Footer
st.markdown("---")
st.markdown("""
in productions
""", unsafe_allow_html=True)

# Auto-refresh for real-time updates (only when recording or speaking)
if st.session_state.recording or st.session_state.is_speaking:
    time.sleep(0.5)
    st.rerun()