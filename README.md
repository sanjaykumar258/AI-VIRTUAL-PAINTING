# AI Virtual Canvas — Enhanced Edition 🎨

A cutting-edge virtual painting application leveraging **OpenCV**, **MediaPipe**, and a **multi-threaded Web Dashboard** to draw on a digital canvas using real-time hand tracking and modern gestures.

---

## 🚀 Key Enhancements

### 1. High-Accuracy Drawing & Tracking
- **EMA Smoothing**: Powered by an Exponential Moving Average algorithm that eliminates hand jitter for silky-smooth brush strokes.
- **Sub-pixel Interpolation**: Automatically fills in line segments when moving quickly, preventing broken lines or gaps.
- **Temporal Debouncing**: Prevents accidental transitions between modes by verifying gestures across frames.

### 2. Multi-threaded Web Dashboard
- **Concurrently Powered**: Upgraded server back-end to a Python `ThreadingHTTPServer` to allow continuous MJPEG video streaming without blocking other concurrent page loads or status requests.
- **Real-time Sync**: Bi-directional control syncs brush sizes, colors, and application state instantly.
- **Cache-Busted Assets**: Integrated automatic cache-prevention headers so browser reloads update instantly.

### 3. Expanded Feature Set
- **Eraser Mode**: Eraser tool size dynamically scales up to wipe away errors easily.
- **Undo System**: Erase the last drawn stroke directly from the UI or via standard shortcuts.
- **Artwork Saving**: Exports drawing canvases on a clean white background straight into the `saved/` folder.

---

## 📁 Project Structure

```
AI-VIRTUAL-PAINTING-main/
├── backend/
│   ├── main.py            # OpenCV pipeline & hand tracking controller
│   ├── server.py          # Concurrency-supporting multi-threaded HTTP server
│   └── requirements.txt   # Third-party package specifications
├── frontend/
│   ├── index.html         # Glassmorphic dark theme dashboard
│   ├── style.css          # Fluid UI grid styling & responsive transitions
│   └── app.js             # API communicator & UI updates
├── saved/                 # Location where paintings are saved (tracked via .gitkeep)
├── README.md              # Project documentation
```

> [!NOTE]
> The `saved/` directory is tracked on Git using a `.gitkeep` file. Individual painting exports are ignored by `.gitignore` so they won't clutter repository commits.

---

## ✋ Gestures Guide

Place your hand clearly inside the camera frame. The application uses the tip of your **Index Finger** as the primary draw indicator and reads modifier fingers:

| Gesture | Hand Pose | Action |
|:---:|---|---|
| **👆 Draw** | Index finger UP only | Draws ink on the canvas |
| **✌️ Hover** | Index + Middle fingers UP | Moves the cursor/hover state without drawing |
| **🤘 Erase** | Index + Pinky fingers UP | Temporarily erases drawing lines |
| **✋ Clear** | All fingers UP | Wipes the entire canvas clear |

---

## ⌨️ Shortcuts Reference

You can run shortcuts in both the OpenCV frame window and the web browser:

| Action | Web UI Button | OpenCV Key | Keyboard Shortcut |
|---|---|:---:|---|
| **Undo** | `Undo` | | `Ctrl + Z` |
| **Save** | `Save` | `S` | `S` |
| **Clear** | `Clear` | `C` | |
| **Eraser** | `Eraser` | `E` | |
| **Select Colors** | Swatches 1–8 | `1` to `8` | |
| **Quit** | | `Q` | |

---

## 🛠️ Quick Start

### 1. Install Dependencies
Make sure Python is installed, then run the installer from the `backend/` folder:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Application
Start the controller server:
```bash
python main.py
```

### 3. Open the Dashboard
Navigate to the local dashboard address in your web browser:
```
http://localhost:5000
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---
*Happy painting!* 🎨
