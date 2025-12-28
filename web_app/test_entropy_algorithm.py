"""
Test script for Entropy Minimization Algorithm
Demonstrates the entropy calculation and optimization process
"""

import numpy as np
import sys
sys.path.insert(0, '.')
from app import PianoTuner

def create_test_data():
    """Create realistic test data for piano tuning"""
    tuner = PianoTuner()
    
    # Simulate recording several keys with realistic inharmonicity
    test_keys = [20, 30, 40, 48, 55, 65, 75]  # Sample keys across the range
    
    for key_idx in test_keys:
        key = tuner.piano_data['keys'][key_idx]
        
        # Simulate a slight deviation from theoretical (realistic piano stretch)
        octaves_from_a4 = (key_idx - 48) / 12.0
        stretch_cents = octaves_from_a4 * 1.5  # Typical piano stretch
        stretch_factor = 2 ** (stretch_cents / 1200)
        
        recorded_freq = key['theoretical_frequency'] * stretch_factor
        key['recorded_frequency'] = recorded_freq
        key['recorded'] = True
        
        # Generate realistic spectral peaks with inharmonicity
        # Inharmonicity coefficient (higher for bass, lower for treble)
        if key_idx < 30:
            B = 0.0008  # Bass strings have more inharmonicity
        elif key_idx < 60:
            B = 0.0003  # Mid-range
        else:
            B = 0.0001  # Treble
        
        # Generate partials with inharmonicity
        peaks = []
        for n in range(1, 6):  # First 5 partials
            # Inharmonic partial frequency: f_n = n·f_0·√(1 + B·n²)
            partial_freq = n * recorded_freq * np.sqrt(1 + B * n**2)
            
            # Magnitude decreases with partial number
            magnitude = 1000.0 / (n**1.5)
            
            peaks.append({
                'frequency': partial_freq,
                'magnitude': magnitude
            })
        
        key['peaks'] = peaks
    
    return tuner

def test_entropy_calculation():
    """Test the entropy minimization algorithm"""
    print("=" * 70)
    print("Testing Entropy Minimization Algorithm")
    print("=" * 70)
    
    # Create test data
    print("\n1. Creating test data with realistic inharmonicity...")
    tuner = create_test_data()
    
    recorded_count = sum(1 for k in tuner.piano_data['keys'] if k['recorded'])
    print(f"   Created {recorded_count} recorded keys with spectral peaks")
    
    # Display some test data
    print("\n2. Sample key data:")
    sample_key = tuner.piano_data['keys'][48]  # A4
    print(f"   Key: {sample_key['name']} (A4)")
    print(f"   Theoretical frequency: {sample_key['theoretical_frequency']:.2f} Hz")
    print(f"   Recorded frequency: {sample_key['recorded_frequency']:.2f} Hz")
    print(f"   Number of peaks: {len(sample_key['peaks'])}")
    
    # Show inharmonicity
    if sample_key['peaks']:
        print(f"   First 3 partials:")
        for i, peak in enumerate(sample_key['peaks'][:3], 1):
            expected = i * sample_key['recorded_frequency']
            deviation = peak['frequency'] - expected
            print(f"     Partial {i}: {peak['frequency']:.2f} Hz "
                  f"(expected: {expected:.2f} Hz, deviation: {deviation:+.2f} Hz)")
    
    # Mock socketio emit function for testing
    progress_log = []
    def mock_emit(event, data):
        if event == 'calculation_progress':
            progress_log.append((data['progress'], data.get('message', '')))
            print(f"\r   Progress: {data['progress']:.0f}% - {data.get('message', '')}", end='')
    
    # Run entropy minimization
    print("\n\n3. Running Entropy Minimization Algorithm...")
    try:
        tuner.calculate_entropy_tuning_curve(socketio_emit=mock_emit)
        print("\n   ✓ Algorithm completed successfully!")
    except Exception as e:
        print(f"\n   ✗ Algorithm failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n4. Results:")
    print("\n   Computed tuning curve (sample keys):")
    print(f"   {'Key':<8} {'Name':<6} {'Theoretical':<12} {'Computed':<12} {'Deviation':<12}")
    print(f"   {'-'*8} {'-'*6} {'-'*12} {'-'*12} {'-'*12}")
    
    sample_indices = [0, 20, 40, 48, 60, 80, 87]
    for idx in sample_indices:
        key = tuner.piano_data['keys'][idx]
        print(f"   {idx:<8} {key['name']:<6} "
              f"{key['theoretical_frequency']:<12.2f} "
              f"{key['computed_frequency']:<12.2f} "
              f"{key.get('tuning_deviation', 0):<12.2f} cents")
    
    # Calculate and display stretch curve
    print("\n5. Tuning stretch analysis:")
    deviations = []
    for i, key in enumerate(tuner.piano_data['keys']):
        if key['computed_frequency'] and key['theoretical_frequency']:
            cents = 1200 * np.log2(key['computed_frequency'] / key['theoretical_frequency'])
            deviations.append(cents)
    
    if deviations:
        print(f"   Average deviation: {np.mean(deviations):.2f} cents")
        print(f"   Max stretch (treble): {np.max(deviations):.2f} cents")
        print(f"   Max compression (bass): {np.min(deviations):.2f} cents")
        print(f"   Curve smoothness (std of differences): "
              f"{np.std(np.diff(deviations)):.2f} cents")
    
    # Verify A4 constraint
    a4_key = tuner.piano_data['keys'][48]
    a4_deviation = 1200 * np.log2(a4_key['computed_frequency'] / a4_key['theoretical_frequency'])
    print(f"\n6. Constraint verification:")
    print(f"   A4 deviation from 440 Hz: {a4_deviation:.4f} cents")
    print(f"   {'✓' if abs(a4_deviation) < 0.01 else '✗'} A4 constraint satisfied")
    
    # Check smoothness
    if len(deviations) > 1:
        max_jump = np.max(np.abs(np.diff(deviations)))
        print(f"   Max jump between adjacent keys: {max_jump:.2f} cents")
        print(f"   {'✓' if max_jump < 5.0 else '✗'} Smoothness constraint satisfied")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)

if __name__ == '__main__':
    test_entropy_calculation()
