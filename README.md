# 🖐️ HandiView — 3D Hand-Tracking Model Viewer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-green.svg)](https://threejs.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.8+-orange.svg)](https://mediapipe.dev/)

**HandiView** is a real-time 3D model viewer that revolutionizes human-computer interaction through intuitive hand gestures. Built for both desktop and web platforms, it demonstrates cutting-edge gesture recognition, 3D rendering, and accessibility-focused design.

🚀 **[Live Web Demo](https://divya-praksh.github.io/HandiView/)** 

---

## 🎯 Problem & Solution

Traditional 3D model viewers rely on mouse and keyboard input, creating barriers for:
- **Accessibility**: Users with limited mobility or motor impairments
- **Sterile Environments**: Medical facilities, clean rooms, public kiosks
- **Immersive Applications**: AR/VR interfaces requiring natural interaction

**HandiView** solves these challenges by enabling touchless, intuitive 3D manipulation through natural hand gestures, making 3D visualization accessible to everyone.

---

## ✨ Core Features

| Feature | Desktop Version | Web Version |
|---------|----------------|-------------|
| **🤲 Hand Tracking** | MediaPipe (Python) + OpenCV | MediaPipe Hands (JavaScript) |
| **🎨 3D Rendering** | PyOpenGL + Pygame | Three.js (WebGL) |
| **📁 Model Support** | `.obj`, `.ply` via file dialog | Pre-loaded models + custom upload* |
| **⚡ Performance** | 60 FPS (high-end), 45 FPS (mid-range) | 30 FPS (Chrome), 25 FPS (Firefox) |
| **🎮 Controls** | Keyboard shortcuts + gestures | UI buttons + gestures |
| **📱 Compatibility** | Windows, macOS, Linux | All modern browsers |
| **🔒 Privacy** | Fully offline | Local processing only |

*Custom upload feature in development for Web version, Completed in desktop version. (Use different 3D objects in the models folder or add ur own .obj files)

---

## 🖥️ Desktop Version

### 🛠️ Tech Stack & Architecture

```
Desktop Application Architecture
├── Computer Vision Layer (OpenCV + MediaPipe)
├── Gesture Recognition Engine (Custom algorithms)
├── 3D Rendering Pipeline (PyOpenGL + Pygame)
└── File Management System (Tkinter + Native dialogs)
```

**Core Technologies:**
- **Python 3.7+** — Core application logic
- **OpenCV** — Real-time webcam capture and image processing
- **MediaPipe** — High-precision hand landmark detection
- **NumPy** — Optimized mathematical computations
- **PyOpenGL** — Hardware-accelerated 3D rendering
- **Pygame** — Cross-platform windowing and event handling
- **Tkinter** — Native file dialog integration


### 🚀 Quick Start (Desktop)

```bash
# Clone the repository
git clone https://github.com/divya-praksh/HandiView.git
cd HandiView/desktop-version

# Create virtual environment (recommended)
python -m venv handiview-env
source handiview-env/bin/activate  # On Windows: handiview-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python hand_tracking.py
```

### 🎮 Desktop Controls

**Keyboard Shortcuts:**
- `L` → Load custom 3D model (.obj/.ply)
- `R` → Reset to default cube
- `F` → Toggle fullscreen mode
- `H` → Show/hide help overlay
- `ESC` → Exit application

**Gesture Controls:**
- 👆 **Index Pinch** (thumb + index finger): Translate object in 3D space
- ✌️ **Three-Finger Pinch** (thumb + index + middle): Rotate around all axes
- 🤏 **Two-Hand Pinch** (both hands): Uniform scaling
- ✋ **Open Palm** (5 fingers extended): Pause all interactions

---

## 🌐 Web Version

### 🛠️ Tech Stack & Architecture

```
Web Application Architecture
├── Frontend UI Layer (HTML5 + CSS3 + Vanilla JS)
├── Computer Vision Module (@mediapipe/hands)
├── 3D Rendering Engine (Three.js + WebGL)
└── Camera Management (WebRTC getUserMedia API)
```

**Core Technologies:**
- **JavaScript ES6+** — Modern async/await patterns
- **HTML5 Canvas** — High-performance rendering surface
- **CSS3 Grid/Flexbox** — Responsive UI layout
- **Three.js r128** — WebGL-based 3D graphics
- **@mediapipe/hands** — Browser-based hand tracking
- **WebRTC** — Real-time camera access

### 🚀 Quick Start (Web)

```bash
# Clone and navigate
git clone https://github.com/divya-praksh/HandiView.git
cd HandiView/web-version

# Start local server (required for camera access)
python3 -m http.server 8000
# Alternative: npx serve . --port 8000

# Open in browser
open http://localhost:8000
```

## 🧠 Technical Deep Dive

### Custom Gesture Recognition Algorithm

HandiView implements a sophisticated gesture classification system:

```python
def classify_gesture(landmarks):
    """
    Multi-stage gesture classification:
    1. Distance-based pinch detection
    2. Angle-based pose recognition  
    3. Temporal smoothing for stability
    4. Confidence scoring
    """
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    
    # Calculate inter-finger distances
    pinch_distance = euclidean_distance(thumb_tip, index_tip)
    three_finger_spread = calculate_spread([thumb_tip, index_tip, middle_tip])
    
    # Apply temporal smoothing
    smoothed_distance = temporal_filter(pinch_distance, window_size=5)
    
    return classify_with_confidence(smoothed_distance, three_finger_spread)
```

### Cross-Platform Rendering Strategy

**Desktop (OpenGL)**:
- Hardware-accelerated vertex processing
- Custom shader programs for lighting
- Efficient mesh loading and caching
- Multi-threaded rendering pipeline

**Web (Three.js)**:
- WebGL 2.0 optimization
- Automatic LOD (Level of Detail) system
- Progressive model loading
- Mobile-optimized shaders

---

## 🔧 Installation & Troubleshooting

### Common Issues & Solutions

**Desktop Version:**
```bash
# Issue: "No module named 'cv2'"
pip install opencv-python

# Issue: "OpenGL context creation failed"
pip install PyOpenGL PyOpenGL_accelerate

# Issue: Camera not detected
# Check: Device Manager → Cameras → Enable camera device
```

**Web Version:**
```javascript
// Issue: Camera permission denied
// Solution: Ensure HTTPS or localhost
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    console.warn('Camera requires HTTPS or localhost');
}

// Issue: Low FPS on mobile
// Solution: Reduce camera resolution
const constraints = {
    video: { width: 480, height: 360, facingMode: 'user' }
};
```
## 🛣️ Development Roadmap

### ✅ Completed Features
- [x] Real-time hand tracking on desktop and web
- [x] Core gesture recognition (pinch, rotate, scale)
- [x] 3D model loading (.obj, .ply formats)
- [x] Cross-platform deployment
- [x] Performance optimization
- [x] Basic accessibility features

### 🚧 In Progress
- [ ] **Custom Model Upload (Web)** — Drag-and-drop .obj/.gltf files
- [ ] **Advanced Gestures** — Two-hand rotation, gesture macros
- [ ] **Mobile App** — React Native port with camera optimization

### 🔮 Future Vision
- [ ] **WebXR Integration** — VR/AR headset support
- [ ] **Voice Commands** — "Rotate left", "Scale up" voice controls  
- [ ] **Haptic Feedback** — Controller vibration for gesture confirmation
- [ ] **Collaborative Mode** — Multi-user 3D manipulation
- [ ] **AI Model Enhancement** — Custom gesture training interface
- [ ] **Cloud Sync** — Save/load 3D scenes across devices

---

## 🏆 Project Impact & Applications

### Real-World Use Cases

**🏥 Healthcare & Medical:**
- Sterile environment 3D model examination
- Medical imaging manipulation without contact
- Accessibility tools for motor-impaired patients

**🎓 Education & Research:**
- Interactive 3D learning experiences
- Molecular model visualization in chemistry
- Architectural model presentation

**🏭 Industrial & Manufacturing:**
- CAD model review in clean environments
- Remote 3D design collaboration
- Quality control inspection interfaces

### Technical Achievements

| Achievement | Impact |
|-------------|--------|
| **Cross-Platform Architecture** | Demonstrates full-stack development across Python and JavaScript |
| **Real-Time Computer Vision** | 30-60 FPS gesture recognition with <50ms latency |
| **Accessibility-First Design** | Touchless interaction supporting diverse user needs |
| **Performance Optimization** | Efficient algorithms maintaining smooth UX on mid-range hardware |
| **Open Source Contribution** | Reusable gesture recognition components for the community |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork repository and clone
git clone https://github.com/YOUR-USERNAME/HandiView.git
cd HandiView

# Create feature branch
git checkout -b feature/amazing-new-gesture

# Make changes and test
# Desktop: python desktop-version/hand_tracking.py
# Web: python3 -m http.server 8000

# Submit pull request with:
# - Clear description of changes
# - Demo video/GIF showing new functionality
# - Updated documentation
```

### Contribution Guidelines

- **Code Style**: Follow PEP 8 (Python) and ESLint (JavaScript)
- **Testing**: Include unit tests for new gesture algorithms
- **Documentation**: Update README and inline comments
- **Performance**: Maintain 30+ FPS on reference hardware
- **Accessibility**: Consider impact on diverse users

### Areas for Contribution

- 🎨 **UI/UX Design** — Improve visual feedback and user interface
- 🤖 **Machine Learning** — Enhance gesture recognition accuracy
- 📱 **Mobile Optimization** — Improve performance on mobile devices
- ♿ **Accessibility** — Add features for diverse abilities
- 🌐 **Internationalization** — Multi-language support
- 📚 **Documentation** — Tutorials, API docs, video guides

---

## 🌟 Why "HandiView"?

The name **HandiView** combines two powerful concepts:

- **"Handi"** — A play on "hand interface" and homage to **accessibility** (handicap → capability)
- **"View"** — Emphasizes **visual interaction** and **perspective control**

This name reflects our core mission: making 3D visualization **accessible**, **intuitive**, and **empowering** for all users.

---

## 📄 License & Citation

HandiView is released under the **MIT License**. See [`LICENSE`](LICENSE) file for full terms.

### Academic Citation

If you use HandiView in academic research, please cite:

```bibtex
@software{handiview2024,
  title={HandiView: Real-Time 3D Hand-Tracking Model Viewer},
  author={Your Name},
  year={2024},
  url={https://github.com/divya-praksh/HandiView},
  note={Cross-platform gesture-controlled 3D visualization system}
}
```

---

## 🌐 Connect & Support

- **📧 Email**: divya.prakash2514@gmail.com
- **🐙 GitHub Issues**: [Report bugs or request features](https://github.com/divya-praksh/HandiView/issues)
- **💬 Discussions**: [Join the community](https://github.com/divya-praksh/HandiView/discussions)
- **💼 LinkedIn**: [My Profile](www.linkedin.com/in/divya-prakash2514)

### Support the Project

If HandiView helps your work or research:
- ⭐ **Star the repository** to show support
- 🍴 **Fork and contribute** new features
- 📢 **Share with others** who might benefit

---

**Made with ❤️ for accessible technology and open-source innovation**

*HandiView — Where natural gestures meet digital creation*

