"""
Converter voor Entropy Piano Tuner JSON bestanden naar nieuwe formaat
"""
import json
import sys

def get_key_name(key_number):
    """Generate key name from key number (0-87)"""
    note_names = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_in_octave = key_number % 12
    note_name = note_names[note_in_octave]
    
    # Octave logic: A, A#, B stay in same octave, then C starts next octave
    if note_in_octave < 3:  # A, A#, B
        octave = key_number // 12
    else:  # C and higher
        octave = key_number // 12 + 1
    
    return f"{note_name}{octave}"

def calculate_theoretical_frequency(key_number):
    """Calculate theoretical frequency for a key (A4 = 440Hz)"""
    return 440.0 * (2 ** ((key_number - 48) / 12))

def convert_ept_to_new_format(old_data):
    """
    Convert old EPT format to new app format
    Old format: id 21-108 (88 keys with offset)
    New format: key_number 0-87
    """
    new_keys = []
    
    for i in range(88):
        old_key_id = i + 21  # Old format starts at key 21
        
        # Find corresponding key in old data
        old_key = None
        for key in old_data:
            if key['id'] == old_key_id:
                old_key = key
                break
        
        theoretical_freq = calculate_theoretical_frequency(i)
        
        if old_key and old_key['mFreq'] > 0 and old_key['isM']:
            # Key was measured
            recorded_freq = old_key['mFreq']
            inharmonicity = old_key.get('inh', 0.0)
            deviation = 1200 * ((recorded_freq / theoretical_freq) ** (1/12) - 1) if theoretical_freq > 0 else 0
            
            new_key = {
                'number': i,
                'name': get_key_name(i),
                'theoretical_frequency': round(theoretical_freq, 2),
                'recorded_frequency': round(recorded_freq, 2),
                'computed_frequency': None,
                'tuning_frequency': round(recorded_freq, 2),
                'tuning_deviation': round(deviation, 2),
                'inharmonicity': inharmonicity,
                'recorded': True,
                'tuned': False,
                'peaks': []
            }
        else:
            # Key not measured
            new_key = {
                'number': i,
                'name': get_key_name(i),
                'theoretical_frequency': round(theoretical_freq, 2),
                'recorded_frequency': None,
                'computed_frequency': None,
                'tuning_frequency': None,
                'tuning_deviation': 0.0,
                'inharmonicity': 0.0,
                'recorded': False,
                'tuned': False,
                'peaks': []
            }
        
        new_keys.append(new_key)
    
    return {'keys': new_keys}

def main():
    if len(sys.argv) < 2:
        print("Gebruik: python convert_ept_format.py <input_file.json> [output_file.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_converted.json')
    
    print(f"Laden: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print(f"Converteren van {len(old_data)} keys...")
    new_data = convert_ept_to_new_format(old_data)
    
    # Count measured keys
    measured_count = sum(1 for key in new_data['keys'] if key['recorded'])
    print(f"✓ {measured_count} gemeten toetsen gevonden")
    
    print(f"Opslaan: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Conversie voltooid!")
    print(f"Je kunt nu '{output_file}' laden in de Piano Tuner app")

if __name__ == '__main__':
    main()
