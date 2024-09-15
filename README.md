# Flask CV App

A web application that integrates computer vision with a 3D model renderer, showcasing how AI/ML tools can be used to enhance web applications. The project uses MediaPipe for hand gesture detection and Pygame with OpenGL for 3D rendering. 

## Features

- Real-time hand gesture detection using MediaPipe
- 3D model rendering with Pygame and OpenGL
- Interactive scaling and rotation of the 3D model based on hand gestures
- Deployable web application using Flask

## Getting Started

### Prerequisites

- Python 3.8 or later
- [Git](https://git-scm.com/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/flask_cv_app.git
   cd flask_cv_app
   
2. **Create and activate a virtual environment**

      ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
      
3. **Install dependencies**

         ```bash
       pip install -r requirements.txt
   
5. **Run the application**
   
         ```bash
       python scripts/main.py

Navigate to http://127.0.0.1:5000 in your browser to view the application.
