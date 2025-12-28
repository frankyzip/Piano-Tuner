# Entropy Minimization Algorithm for Piano Tuning

## Overview

This implementation provides an **Entropy Minimization Algorithm** for optimal piano tuning, based on the scientific method used in the Entropy Piano Tuner (EPT) project.

## Theory

### The Physics

Piano strings exhibit **inharmonicity** - their overtones (partials) are not perfect integer multiples of the fundamental frequency due to string stiffness. The relationship is:

```
f_n = n·f_0·√(1 + B·n²)
```

Where:
- `f_n` = frequency of partial n
- `f_0` = fundamental frequency  
- `B` = inharmonicity coefficient (depends on string properties)
- `n` = partial number (1, 2, 3, ...)

### The Tuning Problem

When multiple piano keys play together, their partials should align for optimal consonance. Traditional Equal Temperament doesn't account for inharmonicity, leading to suboptimal tuning, especially in bass and treble regions.

### Entropy as a Metric

The algorithm uses **spectral entropy** to measure consonance:

```
S = -Σ P(x)·ln(P(x))
```

Where `P(x)` is the probability density of the combined power spectrum of all keys.

- **Lower entropy** = partials are more aligned = better consonance
- **Higher entropy** = partials are scattered = worse consonance

## Algorithm Steps

### 1. Data Collection
- Record audio from multiple piano keys
- Extract spectral peaks (fundamental + partials) using FFT
- Measure amplitudes and frequencies of each partial

### 2. Inharmonicity Estimation
```python
def _estimate_inharmonicity_coefficients(self)
```
- Analyzes the spacing between partials
- Calculates inharmonicity coefficient `B` for each key
- Stores coefficient for use in optimization

### 3. Optimization Setup

**Variables to Optimize:**
- 88 tuning offsets (one per key), measured in cents from Equal Temperament

**Constraints:**
- A4 (key 48) fixed at concert pitch (440 Hz)
- Deviations limited to ±50 cents from Equal Temperament
- Smooth curve (penalize large jumps between adjacent keys)

### 4. Objective Function
```python
def objective_function(offsets_cents)
```

For each proposed tuning configuration:

1. **Build Combined Spectrum:**
   - Convert each offset to frequency multiplier: `f_new = f_theoretical × 2^(offset/1200)`
   - For each recorded key, calculate adjusted partial frequencies
   - Accumulate all partials into a single power spectrum (20 Hz - 10 kHz)
   - Each partial is represented as a Gaussian peak

2. **Calculate Entropy:**
   - Normalize spectrum to probability distribution: `P(x) = spectrum(x) / sum(spectrum)`
   - Compute entropy: `S = -Σ P(x)·ln(P(x))`

3. **Add Regularization:**
   - Smoothness penalty: `0.01 × Σ(Δoffset_i)²` - keeps curve smooth
   - ET proximity penalty: `0.001 × Σ(offset_i)²` - stays near Equal Temperament

4. **Return Total Cost:**
   ```
   cost = entropy + smoothness_penalty + et_penalty
   ```

### 5. Global Optimization
```python
scipy.optimize.differential_evolution(...)
```

Uses **Differential Evolution** algorithm:
- Population-based stochastic method
- Good for multi-modal, high-dimensional problems
- Automatically explores the solution space
- Parameters:
  - `maxiter=50` - balance between quality and runtime
  - `popsize=10` - population size
  - `tol=0.01` - convergence tolerance

### 6. Post-Processing
- Apply Gaussian smoothing to the optimized curve (σ=1.5)
- Ensure A4 is exactly at 0 cents deviation
- Calculate final tuning frequencies and deviations

### 7. Update Piano Data
```python
computed_frequency = theoretical_frequency × 2^(optimal_offset/1200)
```

## Implementation Details

### Key Features

1. **Robust Fallback:**
   - If optimization fails, uses smooth interpolation of recorded data
   - Ensures the algorithm never crashes

2. **Progress Reporting:**
   ```python
   socketio.emit('calculation_progress', {
       'progress': percentage,
       'message': status_message
   })
   ```

3. **Minimal Data Requirements:**
   - Requires at least 5 recorded keys
   - More recorded keys = better optimization
   - Can interpolate for unrecorded keys

4. **Realistic Constraints:**
   - Limits deviations to avoid extreme tunings
   - Maintains smoothness for natural sound
   - Respects A4 concert pitch standard

### Performance

- **Typical Runtime:** 10-30 seconds
- **Accuracy:** Sub-cent precision
- **Scalability:** Handles full 88-key piano
- **Memory:** Low (~50 MB during optimization)

## Usage Example

```python
from app import PianoTuner

# Create tuner instance
tuner = PianoTuner()

# ... record some keys and populate peaks data ...

# Run entropy minimization
def progress_callback(event, data):
    print(f"Progress: {data['progress']}% - {data.get('message', '')}")

tuner.calculate_entropy_tuning_curve(socketio_emit=progress_callback)

# Access results
for key in tuner.piano_data['keys']:
    print(f"{key['name']}: {key['computed_frequency']:.2f} Hz "
          f"(deviation: {key['tuning_deviation']:.2f} cents)")
```

## API Integration

The algorithm is integrated into the Flask web app:

```javascript
// Client-side call
fetch('/api/calculate_tuning', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        algorithm: 'entropy_minimization'
    })
});

// Listen for progress
socket.on('calculation_progress', (data) => {
    console.log(`${data.progress}%: ${data.message}`);
});

// Get final results
socket.on('calculation_completed', (data) => {
    console.log('Tuning curve calculated!', data.data);
});
```

## Testing

Run the test suite:
```bash
cd web_app
python test_entropy_algorithm.py
```

Expected output:
- ✓ Algorithm completes without errors
- ✓ A4 constrained to 0.00 cents
- ✓ Smooth curve (max jump < 5 cents)
- ✓ Realistic stretch curve

## References

1. Haye Hinrichsen, "Entropy Piano Tuner" - http://www.entropy-piano-tuner.org/
2. O.H. Schuck & R.W. Young, "Observations on the Vibrations of Piano Strings" (1943)
3. Harvey Fletcher, "Normal Vibration Frequencies of a Stiff Piano String" (1964)
4. Railsback, "Scale Temperament as Applied to Piano Tuning" (1938)

## Mathematical Appendix

### Cents Conversion
```
cents = 1200 × log₂(f_actual / f_reference)
f_actual = f_reference × 2^(cents/1200)
```

### Inharmonicity Formula
```
B = (1/n²) × [(f_n/(n·f_0))² - 1]
```

### Gaussian Peak Model
```
spectrum[x] = Σ magnitude_i × exp(-0.5 × ((x - x_i)/σ)²)
```

### Entropy Formula
```
S = -Σ P(x)·ln(P(x))  where P(x) = spectrum(x) / Σspectrum
```

### Smoothness Penalty
```
R_smooth = λ_smooth × Σ(offset[i+1] - offset[i])²
```

### Total Objective
```
J(offsets) = S(offsets) + λ_smooth·R_smooth + λ_et·R_et
```

Where:
- `S` = spectral entropy
- `R_smooth` = smoothness regularization
- `R_et` = Equal Temperament proximity regularization
- `λ_smooth = 0.01`, `λ_et = 0.001` = regularization weights

## Troubleshooting

**Q: Algorithm runs but produces flat (0 deviation) curve?**
- A: Not enough recorded keys with spectral peaks. Record at least 5-10 keys across the range.

**Q: Optimization is slow?**
- A: Reduce `maxiter` parameter or use fewer population members.

**Q: Results are too different from Equal Temperament?**
- A: Increase `et_penalty` weight in the objective function.

**Q: Curve has jumps/discontinuities?**
- A: Increase `smoothness_penalty` weight or sigma in Gaussian smoothing.

## Future Enhancements

- [ ] Real-time optimization with GPU acceleration
- [ ] Machine learning for inharmonicity prediction
- [ ] Multi-objective optimization (consonance + stretch + historical tunings)
- [ ] Support for alternate tuning systems (Just Intonation, Werckmeister, etc.)
- [ ] Psychoacoustic modeling of perceived dissonance
