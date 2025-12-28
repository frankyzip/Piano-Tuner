# Entropy Piano Tuner - Web Interface

Een moderne, gebruiksvriendelijke web-interface voor piano stemming gebouwd met Python Flask en WebSockets.

## ✨ Functies

- **🎤 Opname Modus**: Neem piano toetsen op en analyseer hun frequenties
- **🧮 Berekening Modus**: Bereken optimale stemming curves met verschillende algoritmes
  - Equal Temperament
  - Copy Recording (kopieer opgenomen frequenties)
  - Stretch Tuning (met intonatie stretching)
- **🎵 Stem Modus**: Stem je piano met real-time referentie tonen
- **💾 Sessie Management**: Sla je stem sessies op en laad ze later
- **📊 Real-time Feedback**: WebSocket updates voor directe feedback
- **🎹 Visueel Keyboard**: Interactief 88-toetsen piano keyboard

## 🚀 Installatie

### Vereisten

- Python 3.8 of hoger
- Een microfoon voor audio opname
- Luidsprekers of koptelefoon voor referentie tonen

### Stap 1: Installeer Dependencies

```powershell
cd web_app
pip install -r requirements.txt
```

### Stap 2: Start de Applicatie

```powershell
python app.py
```

### Stap 3: Open in Browser

Open je webbrowser en ga naar:
```
http://localhost:5000
```

## 📖 Gebruik

### 1️⃣ Opname Modus

1. Klik op de **"🎤 Opnemen"** knop bovenaan
2. Selecteer een toets op het keyboard
3. Klik op **"🎤 Start Opname"**
4. Speel de corresponderende piano toets (3 seconden opname)
5. De frequentie wordt automatisch geanalyseerd en weergegeven
6. Herhaal voor alle toetsen die je wilt stemmen

### 2️⃣ Berekening Modus

1. Klik op de **"🧮 Berekenen"** knop
2. Selecteer een algoritme:
   - **Equal Temperament**: Standaard gelijkzwevende stemming
   - **Copy Recording**: Gebruik opgenomen frequenties
   - **Stretch Tuning**: Met lichte intonatie correctie
3. Klik op **"🧮 Start Berekening"**
4. Wacht tot de berekening voltooid is

### 3️⃣ Stem Modus

1. Klik op de **"🎵 Stemmen"** knop
2. Selecteer een toets
3. Klik op **"▶️ Speel Referentie"** om de doelfrequentie te horen
4. Stem je piano string naar deze referentie
5. De afwijking wordt real-time weergegeven in cents

### 4️⃣ Sessie Opslaan

1. Klik op **"💾 Opslaan"** in de sidebar
2. Je sessie wordt automatisch opgeslagen met timestamp
3. Om te laden, klik **"📂 Laden"** en voer de bestandsnaam in

## 🎯 Functionaliteit Vergelijking

Deze web interface implementeert alle kernfunctionaliteit van de originele Qt applicatie:

| Functie | Originele App | Web Interface |
|---------|---------------|---------------|
| Audio Opname | ✅ | ✅ |
| Frequentie Analyse | ✅ | ✅ |
| Tuning Algoritmes | ✅ | ✅ |
| Real-time Feedback | ✅ | ✅ |
| Sessie Opslaan | ✅ | ✅ |
| Visueel Keyboard | ✅ | ✅ |
| Multi-platform | ❌ (Qt vereist) | ✅ (Browser-based) |
| Geen Installatie | ❌ | ✅ |
| Modern UI | ❌ | ✅ |

## 🔧 Technische Details

### Backend (Python Flask)

- **Framework**: Flask + Flask-SocketIO
- **Audio**: sounddevice voor opname en afspelen
- **Signal Processing**: SciPy voor FFT en frequentie detectie
- **Real-time Communication**: WebSocket voor live updates

### Frontend (HTML/CSS/JavaScript)

- **Pure JavaScript**: Geen externe frameworks nodig
- **Socket.IO Client**: Voor real-time communicatie
- **Responsive Design**: Werkt op desktop en tablet
- **Modern UI**: Gradient design met smooth animations

### Audio Processing

- **Sample Rate**: 44.1 kHz
- **FFT Analysis**: Hanning window + peak detection
- **Frequency Range**: 20 Hz - 20 kHz
- **Cents Calculation**: Logaritmische pitch vergelijking

## 📊 Algoritmes

### Equal Temperament
Standaard gelijkzwevende stemming waarbij elke halve toon precies een factor 2^(1/12) is.

### Copy Recording
Kopieert de opgenomen frequenties als doelstemming. Nuttig voor het behouden van de huidige karakteristiek van de piano.

### Stretch Tuning
Past lichte intonatie stretching toe, waarbij lage toetsen iets lager en hoge toetsen iets hoger gestemd worden. Dit compenseert voor inharmoniciteit in piano snaren.

## 🐛 Troubleshooting

### Geen audio apparaten gevonden
- Controleer of je microfoon aangesloten en ingeschakeld is
- Geef browser toegang tot microfoon

### Opname werkt niet
- Controleer Python console voor error messages
- Test je microfoon in andere applicaties
- Herstart de Flask server

### Frequentie detectie onnauwkeurig
- Zorg voor een rustige omgeving
- Speel de toets duidelijk en sustained
- Verhoog het volume van je piano

## 🎨 Customization

Je kunt de app aanpassen door:

1. **Kleuren**: Bewerk de CSS variabelen in `templates/index.html`
2. **Algoritmes**: Voeg nieuwe algoritmes toe in `app.py` → `calculate_tuning_curve()`
3. **Sample Rate**: Wijzig `sample_rate` in de `PianoTuner` class
4. **Keyboard Layout**: Pas het aantal toetsen aan in `initialize_piano()`

## 📝 Licentie

Dit is een alternatieve interface voor de Entropy Piano Tuner, die onder GPL v3 licentie valt.

## 🙏 Credits

- Gebaseerd op: Entropy Piano Tuner (Haye Hinrichsen & Christoph Wick)
- Web Interface: 2025 implementatie met moderne web technologieën

## 💡 Voordelen Web Interface

✅ **Geen Qt installatie nodig** - Werkt direct in de browser
✅ **Cross-platform** - Windows, Mac, Linux, zelfs mobiel
✅ **Modern design** - Intuïtieve en aantrekkelijke interface  
✅ **Snel opstarten** - `pip install` en klaar
✅ **Real-time updates** - WebSocket voor instant feedback
✅ **Makkelijk uit te breiden** - Python + JavaScript
✅ **Lichtgewicht** - Minimale dependencies

Veel plezier met stemmen! 🎹🎵
