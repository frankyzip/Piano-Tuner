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
from scipy.optimize import minimize, differential_evolution
from scipy.ndimage import gaussian_filter1d
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
    
    def calculate_entropy_tuning_curve(self, socketio_emit=None):
        """
        Calculate optimal tuning curve using Entropy Minimization Algorithm.
        
        This method implements the core algorithm from the Entropy Piano Tuner (EPT).
        The goal is to minimize the entropy of the combined power spectrum of all piano keys.
        
        Theory:
        - Each piano string produces partials (harmonics) with slight inharmonicity
        - When keys are tuned optimally, their partials align and create consonance
        - Entropy S = -Σ P(x)·ln(P(x)) measures the "disorder" in the spectrum
        - Lower entropy = more aligned partials = better consonance
        
        Args:
            socketio_emit: Function to emit progress updates (optional)
        """
        
        def emit_progress(progress, message=""):
            """Helper to emit progress updates"""
            if socketio_emit:
                socketio_emit('calculation_progress', {
                    'progress': progress,
                    'message': message
                })
        
        emit_progress(0, "Initializing entropy calculation...")
        
        # Step 1: Collect all recorded keys with spectral data
        recorded_keys = []
        for i, key in enumerate(self.piano_data['keys']):
            if key['recorded'] and key['peaks'] and len(key['peaks']) > 0:
                recorded_keys.append(i)
        
        if len(recorded_keys) < 5:
            # Not enough data for entropy minimization, fall back to theoretical
            emit_progress(100, "Insufficient data - using equal temperament")
            for key in self.piano_data['keys']:
                key['computed_frequency'] = key['theoretical_frequency']
                key['tuning_deviation'] = 0.0
            return
        
        emit_progress(5, f"Found {len(recorded_keys)} recorded keys")
        
        # Step 2: Extract inharmonicity coefficients from peaks
        inharmonicity_coefficients = self._estimate_inharmonicity_coefficients()
        emit_progress(10, "Estimated inharmonicity coefficients")
        
        # Step 3: Set up optimization problem
        # We'll optimize the tuning offset (in cents) for each key
        # Constraint: A4 stays fixed, smooth curve, stay close to equal temperament
        
        a4_index = self.piano_data['key_of_a4']
        
        # Initial guess: all keys at equal temperament (offset = 0 cents)
        initial_offsets = np.zeros(88)
        
        # Bounds: limit deviations to ±50 cents from equal temperament
        bounds = [(-50, 50) for _ in range(88)]
        
        # A4 must stay at 0 cents (fixed at concert pitch)
        bounds[a4_index] = (0, 0)
        
        emit_progress(15, "Setting up optimization problem...")
        
        # Step 4: Define the objective function (entropy calculation)
        def objective_function(offsets_cents):
            """
            Calculate total entropy for given tuning offsets.
            
            Args:
                offsets_cents: Array of 88 tuning offsets in cents from equal temperament
            
            Returns:
                float: Total entropy value (to be minimized)
            """
            # Convert offsets to frequency multipliers
            frequency_multipliers = 2.0 ** (offsets_cents / 1200.0)
            
            # Create combined spectrum with all partials
            # Use a frequency grid from 20 Hz to 10 kHz
            freq_min, freq_max = 20.0, 10000.0
            freq_resolution = 0.1  # Hz
            freq_grid = np.arange(freq_min, freq_max, freq_resolution)
            
            # Accumulate power spectrum
            total_spectrum = np.zeros_like(freq_grid)
            
            for key_idx in recorded_keys:
                key = self.piano_data['keys'][key_idx]
                base_freq = key['theoretical_frequency'] * frequency_multipliers[key_idx]
                
                # Get peaks (partials)
                peaks = key['peaks']
                if not peaks:
                    continue
                
                # Estimate fundamental and partial ratios from recorded data
                recorded_fund = key['recorded_frequency']
                if recorded_fund is None or recorded_fund <= 0:
                    continue
                
                # Add each partial to the spectrum
                for peak in peaks:
                    peak_freq_recorded = peak['frequency']
                    peak_magnitude = peak['magnitude']
                    
                    # Calculate partial number and inharmonicity shift
                    partial_ratio = peak_freq_recorded / recorded_fund
                    
                    # Apply the tuning offset to this partial
                    adjusted_peak_freq = base_freq * partial_ratio
                    
                    # Add this partial as a narrow peak (Gaussian) to the spectrum
                    # Width depends on the partial number (higher partials have more width)
                    peak_width = 0.5 + 0.1 * partial_ratio  # Hz
                    
                    # Find the nearest grid point
                    freq_idx = np.searchsorted(freq_grid, adjusted_peak_freq)
                    if 0 < freq_idx < len(freq_grid):
                        # Add Gaussian-shaped peak
                        sigma = peak_width / freq_resolution
                        gaussian_range = int(5 * sigma)
                        start_idx = max(0, freq_idx - gaussian_range)
                        end_idx = min(len(freq_grid), freq_idx + gaussian_range)
                        
                        x = np.arange(start_idx, end_idx)
                        gaussian = peak_magnitude * np.exp(-0.5 * ((x - freq_idx) / sigma) ** 2)
                        total_spectrum[start_idx:end_idx] += gaussian
            
            # Normalize spectrum to create a probability distribution
            spectrum_sum = np.sum(total_spectrum)
            if spectrum_sum > 0:
                P = total_spectrum / spectrum_sum
            else:
                return 1e10  # Very high entropy if no spectrum
            
            # Calculate entropy: S = -Σ P(x)·ln(P(x))
            # Avoid log(0) by filtering out zero probabilities
            P_nonzero = P[P > 1e-12]
            entropy = -np.sum(P_nonzero * np.log(P_nonzero))
            
            # Add regularization terms to enforce constraints
            
            # 1. Smoothness penalty: penalize large jumps between adjacent keys
            smoothness_penalty = np.sum(np.diff(offsets_cents) ** 2) * 0.01
            
            # 2. Equal temperament proximity: penalize large deviations from ET
            et_penalty = np.sum(offsets_cents ** 2) * 0.001
            
            total_cost = entropy + smoothness_penalty + et_penalty
            
            return total_cost
        
        emit_progress(20, "Starting optimization...")
        
        # Step 5: Run optimization
        # Use differential_evolution for global optimization
        # This is more robust than local minimizers for this type of problem
        
        try:
            result = differential_evolution(
                objective_function,
                bounds,
                maxiter=50,  # Limit iterations for reasonable runtime
                popsize=10,
                tol=0.01,
                workers=1,
                updating='deferred',
                callback=lambda xk, convergence: emit_progress(
                    20 + int(60 * min(1.0, convergence)),
                    "Optimizing tuning curve..."
                )
            )
            
            optimal_offsets = result.x
            emit_progress(80, "Optimization complete")
            
        except Exception as e:
            emit_progress(80, f"Optimization failed: {str(e)}, using fallback")
            # Fallback: smooth interpolation of recorded deviations
            optimal_offsets = self._fallback_smooth_tuning(recorded_keys)
        
        # Step 6: Apply smoothing to the result for better curve
        optimal_offsets = gaussian_filter1d(optimal_offsets, sigma=1.5)
        
        # Ensure A4 is exactly at 0
        optimal_offsets[a4_index] = 0.0
        
        emit_progress(85, "Applying tuning curve...")
        
        # Step 7: Update piano data with computed frequencies
        for i, key in enumerate(self.piano_data['keys']):
            # Calculate the tuned frequency
            offset_cents = optimal_offsets[i]
            frequency_multiplier = 2.0 ** (offset_cents / 1200.0)
            computed_freq = key['theoretical_frequency'] * frequency_multiplier
            
            key['computed_frequency'] = round(computed_freq, 2)
            key['tuning_frequency'] = round(computed_freq, 2)
            
            # Calculate deviation from recorded frequency (if available)
            if key['recorded_frequency'] and key['recorded_frequency'] > 0:
                deviation_cents = 1200 * np.log2(key['recorded_frequency'] / computed_freq)
                key['tuning_deviation'] = round(deviation_cents, 2)
            else:
                key['tuning_deviation'] = round(offset_cents, 2)
        
        emit_progress(100, "Entropy tuning calculation complete")
    
    def _estimate_inharmonicity_coefficients(self):
        """
        Estimate inharmonicity coefficient for each key based on recorded peaks.
        
        Inharmonicity coefficient B relates to how much partials deviate from
        perfect harmonics: f_n = n·f_0·√(1 + B·n²)
        
        Returns:
            dict: {key_index: inharmonicity_coefficient}
        """
        inharmonicity = {}
        
        for i, key in enumerate(self.piano_data['keys']):
            if not key['recorded'] or not key['peaks'] or len(key['peaks']) < 2:
                inharmonicity[i] = 0.0
                continue
            
            recorded_fund = key['recorded_frequency']
            if recorded_fund is None or recorded_fund <= 0:
                inharmonicity[i] = 0.0
                continue
            
            # Analyze peaks to estimate inharmonicity
            # For each peak, calculate what partial number it likely represents
            B_estimates = []
            
            for peak in key['peaks'][:5]:  # Use up to 5 strongest peaks
                peak_freq = peak['frequency']
                # Estimate partial number (approximate)
                n = round(peak_freq / recorded_fund)
                
                if n >= 2 and n <= 10:  # Only use reasonable partial numbers
                    # Solve for B: peak_freq = n·fund·√(1 + B·n²)
                    # B = (1/n²)·[(peak_freq/(n·fund))² - 1]
                    ratio = peak_freq / (n * recorded_fund)
                    if ratio > 1.0:  # Inharmonicity makes partials sharp
                        B = (1.0 / n**2) * (ratio**2 - 1.0)
                        if 0 < B < 0.01:  # Reasonable range for piano inharmonicity
                            B_estimates.append(B)
            
            # Average the estimates
            if B_estimates:
                inharmonicity[i] = np.median(B_estimates)
            else:
                inharmonicity[i] = 0.0001  # Small default value
            
            # Store in key data
            key['inharmonicity'] = inharmonicity[i]
        
        return inharmonicity
    
    def _fallback_smooth_tuning(self, recorded_keys):
        """
        Fallback method: create smooth tuning curve by interpolating recorded deviations.
        
        Args:
            recorded_keys: List of key indices that have been recorded
        
        Returns:
            np.array: Tuning offsets in cents for all 88 keys
        """
        # Get recorded deviations
        recorded_deviations = []
        recorded_indices = []
        
        for key_idx in recorded_keys:
            key = self.piano_data['keys'][key_idx]
            if key['recorded_frequency'] and key['theoretical_frequency']:
                deviation = 1200 * np.log2(
                    key['recorded_frequency'] / key['theoretical_frequency']
                )
                recorded_deviations.append(deviation)
                recorded_indices.append(key_idx)
        
        if len(recorded_indices) < 2:
            return np.zeros(88)
        
        # Interpolate to all 88 keys
        all_indices = np.arange(88)
        interpolated = np.interp(
            all_indices,
            recorded_indices,
            recorded_deviations
        )
        
        # Apply smoothing
        smoothed = gaussian_filter1d(interpolated, sigma=2.0)
        
        # Ensure A4 is at 0
        a4_index = self.piano_data['key_of_a4']
        smoothed[a4_index] = 0.0
        
        return smoothed

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
        if algorithm == 'entropy_minimization':
            # Entropy Minimization Algorithm (EPT method)
            tuner.calculate_entropy_tuning_curve(socketio_emit=socketio.emit)
        
        elif algorithm == 'equal_temperament':
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
