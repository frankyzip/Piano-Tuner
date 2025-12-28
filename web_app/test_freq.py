"""
Test piano frequencies
"""

# Key 0 (A0) should be 27.5 Hz
# Key 48 (A4) should be 440 Hz
# Key 39 (C4) should be ~261.63 Hz

def get_freq(key_num):
    key_of_a4 = 48
    semitones_from_a4 = key_num - key_of_a4
    return 440.0 * (2 ** (semitones_from_a4 / 12))

print("=== Verificatie Piano Frequenties ===")
print(f"Key 0  (A0):  {get_freq(0):.2f} Hz (verwacht: 27.50 Hz)")
print(f"Key 3  (C1):  {get_freq(3):.2f} Hz (verwacht: 32.70 Hz)")
print(f"Key 12 (A1):  {get_freq(12):.2f} Hz (verwacht: 55.00 Hz)")
print(f"Key 39 (C4):  {get_freq(39):.2f} Hz (verwacht: 261.63 Hz)")
print(f"Key 48 (A4):  {get_freq(48):.2f} Hz (verwacht: 440.00 Hz)")
print(f"Key 51 (C5):  {get_freq(51):.2f} Hz (verwacht: 523.25 Hz)")
print(f"Key 87 (C8):  {get_freq(87):.2f} Hz (verwacht: 4186.01 Hz)")
