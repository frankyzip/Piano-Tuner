"""
Entropy Piano Tuner - Modern Web Interface
A Flask-based web application for piano tuning
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import numpy as np
import sounddevice as sd
from scipy import signal
from scipy.fft import rfft, rfftfreq
import json
import os
from datetime import datetime
import threading
import queue
import webbrowser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'entropy-piano-tuner-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
class PianoTuner:
    def __init__(self):
        self.mode = 'idle'  # idle, recording, calculating, tuning
        self.piano_data = self.initialize_piano()
        self.audio_buffer = queue.Queue()
        self.recording = False
        self.selected_key = None
        self.sample_rate = 44100
        self.concert_pitch = 440.0
        
    def initialize_piano(self):
        """Initialize piano with 88 keys (standard piano)"""
        piano = {
            'num_keys': 88,
            'key_of_a4': 48,  # A4 is key 49 (0-indexed = 48)
            'concert_pitch': 440.0,
            'keys': []
        }
        
        # Create all 88 keys
        for i in range(88):
            # A4 (key 49, 0-indexed=48) = 440 Hz
            # Each semitone is 2^(1/12) factor
            semitones_from_a4 = i - piano['key_of_a4']
            theoretical_freq = 440.0 * (2 ** (semitones_from_a4 / 12))
            
            key_data = {
                'number': i,
                'name': self.get_key_name(i),
                'theoretical_frequency': theoretical_freq,
                'recorded_frequency': None,
                'computed_frequency': None,
                'tuning_deviation': 0.0,
                'recorded': False,
                'peaks': []
            }
            piano['keys'].append(key_data)
        
        return piano
    
    def get_key_name(self, key_number):
        """Convert key number to note name (e.g., 48 -> A4)"""
        notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        # Piano key 0 = A0 (27.5 Hz)
        # Octaves change at C, so C after A0/B0 is C1
        note_index = key_number % 12
        # A0, A#0, B0 are octave 0, then C1 starts octave 1
        if note_index >= 0 and note_index <= 2:  # A, A#, B
            octave = key_number // 12
        else:  # C through G#
            octave = (key_number // 12) + 1
        return f"{notes[note_index]}{octave}"
    
    def get_key(self, key_number):
        """Get key data by number"""
        if 0 <= key_number < len(self.piano_data['keys']):
            return self.piano_data['keys'][key_number]
        return None

# Global tuner instance
tuner = PianoTuner()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/piano_data')
def get_piano_data():
    """Get current piano data"""
    return jsonify(tuner.piano_data)

@app.route('/api/mode', methods=['GET', 'POST'])
def mode_control():
    """Get or set current mode"""
    if request.method == 'POST':
        new_mode = request.json.get('mode')
        if new_mode in ['idle', 'recording', 'calculating', 'tuning']:
            tuner.mode = new_mode
            socketio.emit('mode_changed', {'mode': new_mode})
            return jsonify({'success': True, 'mode': new_mode})
        return jsonify({'success': False, 'error': 'Invalid mode'}), 400
    
    return jsonify({'mode': tuner.mode})

@app.route('/api/select_key', methods=['POST'])
def select_key():
    """Select a piano key"""
    key_number = request.json.get('key_number')
    if 0 <= key_number < tuner.piano_data['num_keys']:
        tuner.selected_key = key_number
        key_data = tuner.get_key(key_number)
        socketio.emit('key_selected', {'key_number': key_number, 'key_data': key_data})
        return jsonify({'success': True, 'key': key_data})
    return jsonify({'success': False, 'error': 'Invalid key number'}), 400

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    """Start recording audio for the selected key"""
    if tuner.selected_key is None:
        return jsonify({'success': False, 'error': 'No key selected'}), 400
    
    # Start recording in a separate thread
    threading.Thread(target=record_audio, args=(tuner.selected_key,), daemon=True).start()
    
    return jsonify({'success': True, 'message': 'Recording started'})

def record_audio(key_number, duration=3.0):
    """Record audio and analyze frequency"""
    tuner.recording = True
    socketio.emit('recording_started', {'key_number': key_number})
    
    try:
        # Record audio
        recording = sd.rec(int(duration * tuner.sample_rate), 
                          samplerate=tuner.sample_rate, 
                          channels=1, 
                          dtype='float32')
        sd.wait()
        
        # Analyze frequency
        audio_data = recording.flatten()
        frequency, peaks = analyze_frequency(audio_data, tuner.sample_rate)
        
        # Update key data
        key = tuner.get_key(key_number)
        if key:
            key['recorded_frequency'] = frequency
            key['recorded'] = True
            key['peaks'] = peaks
            
            # Calculate deviation from theoretical
            if frequency:
                cents = 1200 * np.log2(frequency / key['theoretical_frequency'])
                key['tuning_deviation'] = cents
        
        socketio.emit('recording_completed', {
            'key_number': key_number,
            'frequency': frequency,
            'deviation': key['tuning_deviation'] if key else 0
        })
        
    except Exception as e:
        socketio.emit('recording_error', {'error': str(e)})
    
    finally:
        tuner.recording = False

def analyze_frequency(audio_data, sample_rate):
    """Analyze audio to detect fundamental frequency"""
    # Apply window to reduce spectral leakage
    window = signal.windows.hann(len(audio_data))
    audio_windowed = audio_data * window
    
    # Compute FFT
    fft_data = rfft(audio_windowed)
    freqs = rfftfreq(len(audio_windowed), 1/sample_rate)
    magnitude = np.abs(fft_data)
    
    # Find peaks
    peak_indices, properties = signal.find_peaks(magnitude, height=np.max(magnitude)*0.1)
    
    if len(peak_indices) == 0:
        return None, []
    
    # Get the fundamental (lowest strong peak)
    peaks = []
    for idx in peak_indices[:10]:  # Top 10 peaks
        if freqs[idx] > 20:  # Ignore very low frequencies
            peaks.append({
                'frequency': float(freqs[idx]),
                'magnitude': float(magnitude[idx])
            })
    
    # Sort by magnitude
    peaks.sort(key=lambda x: x['magnitude'], reverse=True)
    
    # Fundamental is usually the strongest peak or lowest significant peak
    if peaks:
        fundamental = peaks[0]['frequency']
        return fundamental, peaks[:5]
    
    return None, []

@app.route('/api/calculate_tuning', methods=['POST'])
def calculate_tuning():
    """Calculate optimal tuning curve"""
    algorithm = request.json.get('algorithm', 'equal_temperament')
    
    # Start calculation in background
    threading.Thread(target=calculate_tuning_curve, args=(algorithm,), daemon=True).start()
    
    return jsonify({'success': True, 'message': 'Calculation started'})

def calculate_tuning_curve(algorithm='equal_temperament'):
    """Calculate tuning curve using specified algorithm"""
    socketio.emit('calculation_started', {'algorithm': algorithm})
    
    try:
        if algorithm == 'equal_temperament':
            # Equal temperament: use theoretical frequencies
            total_keys = len(tuner.piano_data['keys'])
            for i, key in enumerate(tuner.piano_data['keys']):
                key['computed_frequency'] = key['theoretical_frequency']
                key['tuning_frequency'] = key['theoretical_frequency']
                # Calculate deviation from theoretical
                if key['recorded_frequency']:
                    cents = 1200 * np.log2(key['recorded_frequency'] / key['theoretical_frequency'])
                    key['tuning_deviation'] = round(cents, 2)
                progress = (i + 1) / total_keys * 100
                socketio.emit('calculation_progress', {'progress': progress})
        
        elif algorithm == 'copy_recording':
            # Copy recorded frequencies
            total_keys = len(tuner.piano_data['keys'])
            for i, key in enumerate(tuner.piano_data['keys']):
                if key['recorded_frequency']:
                    key['computed_frequency'] = key['recorded_frequency']
                    key['tuning_frequency'] = key['recorded_frequency']
                    # Deviation is 0 since we're using recorded as target
                    key['tuning_deviation'] = 0.0
                else:
                    key['computed_frequency'] = key['theoretical_frequency']
                    key['tuning_frequency'] = key['theoretical_frequency']
                    key['tuning_deviation'] = 0.0
                progress = (i + 1) / total_keys * 100
                socketio.emit('calculation_progress', {'progress': progress})
        
        elif algorithm == 'stretch_tuning':
            # Simple stretch tuning (exaggerates deviations slightly)
            total_keys = len(tuner.piano_data['keys'])
            for i, key in enumerate(tuner.piano_data['keys']):
                if key['recorded_frequency']:
                    stretch_factor = 1.0 + (abs(i - 48) * 0.0001)  # Slight stretch
                    key['computed_frequency'] = key['theoretical_frequency'] * stretch_factor
                    key['tuning_frequency'] = key['theoretical_frequency'] * stretch_factor
                    # Calculate deviation from recorded
                    cents = 1200 * np.log2(key['computed_frequency'] / key['recorded_frequency'])
                    key['tuning_deviation'] = round(cents, 2)
                else:
                    key['computed_frequency'] = key['theoretical_frequency']
                    key['tuning_frequency'] = key['theoretical_frequency']
                    key['tuning_deviation'] = 0.0
                progress = (i + 1) / total_keys * 100
                socketio.emit('calculation_progress', {'progress': progress})
        
        elif algorithm == 'inharmonicity':
            # Inharmonicity-based tuning: optimal stretch based on measured inharmonicity
            total_keys = len(tuner.piano_data['keys'])
            for i, key in enumerate(tuner.piano_data['keys']):
                inh = key.get('inharmonicity', 0.0)
                
                # Calculate stretch based on inharmonicity coefficient
                # Formula based on Railsback curve and inharmonicity physics
                # Higher inharmonicity requires more stretch
                octaves_from_a4 = (i - 48) / 12.0
                
                if inh > 0:
                    # Stretch increases with distance from A4 and inharmonicity
                    # This is a simplified model - professional tuners use more complex formulas
                    stretch_cents = octaves_from_a4 * (inh * 5000)  # Scale factor based on typical piano values
                    stretch_ratio = 2 ** (stretch_cents / 1200)
                    tuning_freq = key['theoretical_frequency'] * stretch_ratio
                else:
                    # No inharmonicity data, use theoretical
                    tuning_freq = key['theoretical_frequency']
                
                key['computed_frequency'] = round(tuning_freq, 2)
                key['tuning_frequency'] = round(tuning_freq, 2)
                
                # Calculate deviation from recorded (if available)
                if key['recorded_frequency']:
                    cents = 1200 * np.log2(key['recorded_frequency'] / tuning_freq)
                    key['tuning_deviation'] = round(cents, 2)
                else:
                    key['tuning_deviation'] = 0.0
                    
                progress = (i + 1) / total_keys * 100
                socketio.emit('calculation_progress', {'progress': progress})
        
        socketio.emit('calculation_completed', {'success': True, 'data': tuner.piano_data})
        
    except Exception as e:
        socketio.emit('calculation_error', {'error': str(e)})

@app.route('/api/play_tone', methods=['POST'])
def play_tone():
    """Play a synthesized tone for a key"""
    key_number = request.json.get('key_number')
    use_computed = request.json.get('use_computed', True)
    
    key = tuner.get_key(key_number)
    if not key:
        return jsonify({'success': False, 'error': 'Invalid key'}), 400
    
    frequency = key['computed_frequency'] if use_computed else key['theoretical_frequency']
    if frequency:
        threading.Thread(target=play_synthesized_tone, args=(frequency,), daemon=True).start()
        return jsonify({'success': True, 'frequency': frequency})
    
    return jsonify({'success': False, 'error': 'No frequency available'}), 400

def play_synthesized_tone(frequency, duration=2.0):
    """Generate and play a sine wave at the given frequency"""
    t = np.linspace(0, duration, int(tuner.sample_rate * duration))
    
    # Create a more pleasant sound with overtones
    wave = np.sin(2 * np.pi * frequency * t)  # Fundamental
    wave += 0.3 * np.sin(2 * np.pi * 2 * frequency * t)  # 2nd harmonic
    wave += 0.15 * np.sin(2 * np.pi * 3 * frequency * t)  # 3rd harmonic
    
    # Apply envelope (fade in/out)
    envelope = np.ones_like(t)
    fade_samples = int(0.05 * tuner.sample_rate)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    wave = wave * envelope * 0.3  # Scale volume
    
    sd.play(wave, tuner.sample_rate)
    sd.wait()

@app.route('/api/save_session', methods=['POST'])
def save_session():
    """Save current piano tuning session"""
    filename = request.json.get('filename', f'piano_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    filepath = os.path.join('sessions', filename)
    os.makedirs('sessions', exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(tuner.piano_data, f, indent=2)
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/load_session', methods=['POST'])
def load_session():
    """Load a saved piano tuning session"""
    filename = request.json.get('filename')
    filepath = os.path.join('sessions', filename)
    
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    with open(filepath, 'r') as f:
        tuner.piano_data = json.load(f)
    
    socketio.emit('session_loaded', tuner.piano_data)
    return jsonify({'success': True, 'data': tuner.piano_data})

@app.route('/api/load_session_data', methods=['POST'])
def load_session_data():
    """Load piano tuning session from uploaded JSON data"""
    data = request.json.get('data')
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    tuner.piano_data = data
    socketio.emit('session_loaded', tuner.piano_data)
    return jsonify({'success': True, 'data': tuner.piano_data})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'mode': tuner.mode, 'piano_data': tuner.piano_data})

def open_browser(port):
    """Open browser after a short delay"""
    import time
    time.sleep(2)
    webbrowser.open(f'http://localhost:{port}')

if __name__ == '__main__':
    port = 5555
    print("=" * 60)
    print("Entropy Piano Tuner - Web Interface")
    print("=" * 60)
    print("Starting server...")
    print(f"Browser will open at: http://localhost:{port}")
    print("=" * 60)
    
    # Open browser in background
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    # Start server
    socketio.run(app, host='127.0.0.1', port=port, debug=False, allow_unsafe_werkzeug=True)
