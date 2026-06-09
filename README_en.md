<p align="center">
  <img src="assets/readme/pets/hero.png" width="450" alt="Desktop Pet App Hero">
</p>

# 🐾 Desktop Pet App – Demo Edition  
A desktop pet that reacts to your smile and voice.  
This demo includes 8 fully pre‑configured pets.

---

# 📥 Setup (GitHub Edition – Python Required)

This GitHub edition is intended for **developers** and requires Python.  
(For the Portable Edition with embedded Python, no setup is required.)

---

## 1. Install Python (Required)

Install **Python 3.10–3.11** from the link below:

🔗 https://www.python.org/downloads/windows/

Be sure to:

- Check **Add Python to PATH**  
- Select **Install for all users** (recommended)

⚠ Important Notes  
- Having Python 3.12 installed is fine  
- However, this app only works with **Python 3.10–3.11**  
- `create_venv.bat` uses the python.exe found in PATH  
- Therefore, Python 3.10–3.11 must be installed

---

## 2. Download ZIP

1. Click **“Code”** (top right)  
2. Select **“Download ZIP”**  
3. Extract the ZIP

---

## 3. ffmpeg (Included)

The `ffmpeg/` folder already contains:

- ffmpeg.exe  
- ffprobe.exe  

No additional downloads are required.

---

## 4. Create Virtual Environment

Run **create_venv.bat** inside the extracted folder.

- Required libraries will be installed automatically  
- PyTorch (CPU version) will also be installed  

---

## 5. Launch the App

```
run_pet.bat
```

---

# 🌟 About This App

This application is an  
**AI‑powered desktop pet that reacts to your smile, voice, and gestures.**

- 8 pets are pre‑registered  
- 14 states (n1–p11) can be switched freely  
- Whisper‑based speech recognition  
- Camera‑based smile & gesture detection  
- All images, videos, and audio files are included

---

# 🐾 Included Pets (8)

| Name | Species | Folder |
|------|---------|--------|
| John | Dog | `assets/john/` |
| Kuro | Rabbit | `assets/kuro/` |
| Marple | Dog | `assets/marple/` |
| Mary | Dog | `assets/mary/` |
| Shiro | Cat | `assets/shiro/` |
| Tama | Cat | `assets/tama/` |
| Taro | Dog | `assets/taro/` |
| Usako | Rabbit | `assets/usako/` |

---

# 🐾 State List (n1–p11)

| Code | Name | Description | Thumbnail |
|------|------|-------------|-----------|
| n1 | Normal | The pet is in a normal, waiting state. | states/n1.png |
| n2 | Sitting | The pet is sitting in place in response to the owner's command. | states/n2.png |
| n3 | Sleeping | The pet is lying down to rest or sleep. | states/n3.png |
| p1 | Playing | Active behavior such as playing or going for a walk. | states/p1.png |
| p2 | Joy | A joyful gesture (species‑specific details below). | states/p2.png |
| p3 | Down | The pet is in a down position. | states/p3.png |
| p4 | Paw | Raising one paw in response to the owner's command. | states/p4.png |
| p5 | Food | Eating gesture or appearance. | states/p5.png |
| p6 | Water | Drinking gesture or appearance. | states/p6.png |
| p7 | Toilet | Sitting on the pet toilet. | states/p7.png |
| p8 | Fetch | Fetching a ball or object. | states/p8.png |
| p9 | House | Entering or staying in the crate/house. | states/p9.png |
| p10 | Chin | Standing‑up gestures such as “Chin Chin” or “Stand Up”. | states/p10.png |
| p11 | Bath | Bathing, brushing, grooming scenes. | states/p11.png |

---

## 🐶 Species‑Specific Details for Joy (p2)

### Dog  
Expressing joy by wagging its tail vigorously, tilting its ears back slightly, narrowing its eyes, and lightly lifting its front paws while running toward the owner.

### Cat  
Expressing joy by narrowing its eyes, holding its tail straight up with a slight wag, tilting its head, and rubbing its body against the owner.

### Rabbit  
Expressing joy by shaking its head and ears vigorously and performing a big “binky” jump.

---

# 🎞 Demo (GIF)

![demo](assets/readme/pets/demo.gif)

---

# 📸 Screenshots

![main](assets/readme/pets/welcome.png)

---

# 🗂 Folder Structure

```
DesktopPetApp_github/
├─ assets/
├─ data/
├─ ui/
├─ core/
├─ utils/
├─ ffmpeg/
├─ desktop_pet_app.py
├─ requirements.txt
├─ create_venv.bat
├─ run_pet.bat
├─ CREDITS.md
├─ LICENSE
└─ README.md
```

---

# 🛠 Technical Stack

- PySide6 (UI)  
- pygame (animation)  
- OpenCV (camera detection)  
- ffmpeg (video processing)  
- Whisper (speech recognition)  
- Python 3.10+  
- No GPU required (CPU only)

---

# 🖥 System Requirements

- Windows 10 / 11  
- Python 3.10–3.11  
- Webcam  
- Microphone  
- ffmpeg included  
- No GPU required

---

# 🎉 Summary

This application is a  
**fully‑featured desktop pet demo with 8 ready‑to‑use pets.**

If you want to register your own pet and enjoy a personalized experience,  
please use:

**PetApp2 – portable / shelly / mimi / peter (User Version)**.
```

---

