import cv2
import mediapipe as mp
import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog
import os
import threading

class Model3D:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.edges = []
        self.normals = []
        self.has_model = False
        self.model_name = "Default Cube"
        
    def load_default_cube(self):
        """Load default cube when no model is provided"""
        self.vertices = [
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],  # Back face
            [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]   # Front face
        ]
        
        self.faces = [
            [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [2, 6, 7, 3],  # Back, Front, Bottom, Top
            [0, 3, 7, 4], [1, 5, 6, 2]  # Left, Right
        ]
        
        self.edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Back face
            [4, 5], [5, 6], [6, 7], [7, 4],  # Front face
            [0, 4], [1, 5], [2, 6], [3, 7]   # Connecting edges
        ]
        
        self.has_model = True
        self.model_name = "Default Cube"
        
    def load_obj_file(self, filepath):
        """Load OBJ file format"""
        try:
            self.vertices = []
            self.faces = []
            self.edges = []
            
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('v '):  # Vertex
                        parts = line.split()
                        vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                        self.vertices.append(vertex)
                    elif line.startswith('f '):  # Face
                        parts = line.split()[1:]  # Skip 'f'
                        face = []
                        for part in parts:
                            # Handle vertex/texture/normal format (v/vt/vn or v//vn or just v)
                            vertex_index = int(part.split('/')[0]) - 1  # OBJ uses 1-based indexing
                            face.append(vertex_index)
                        if len(face) >= 3:  # Valid face needs at least 3 vertices
                            self.faces.append(face)
            
            # Generate edges from faces
            self.generate_edges_from_faces()
            
            # Normalize the model to fit in a reasonable size
            self.normalize_model()
            
            self.has_model = True
            self.model_name = os.path.basename(filepath)
            print(f"Loaded model: {self.model_name}")
            print(f"Vertices: {len(self.vertices)}, Faces: {len(self.faces)}")
            return True
            
        except Exception as e:
            print(f"Error loading OBJ file: {e}")
            self.load_default_cube()  # Fallback to cube
            return False
    
    def load_ply_file(self, filepath):
        """Load PLY file format (basic support)"""
        try:
            self.vertices = []
            self.faces = []
            
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
            # Parse header
            vertex_count = 0
            face_count = 0
            header_end = 0
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('element vertex'):
                    vertex_count = int(line.split()[-1])
                elif line.startswith('element face'):
                    face_count = int(line.split()[-1])
                elif line == 'end_header':
                    header_end = i + 1
                    break
            
            # Read vertices
            for i in range(header_end, header_end + vertex_count):
                parts = lines[i].strip().split()
                vertex = [float(parts[0]), float(parts[1]), float(parts[2])]
                self.vertices.append(vertex)
            
            # Read faces
            for i in range(header_end + vertex_count, header_end + vertex_count + face_count):
                parts = lines[i].strip().split()
                face_vertex_count = int(parts[0])
                face = [int(parts[j+1]) for j in range(face_vertex_count)]
                self.faces.append(face)
            
            self.generate_edges_from_faces()
            self.normalize_model()
            
            self.has_model = True
            self.model_name = os.path.basename(filepath)
            print(f"Loaded PLY model: {self.model_name}")
            return True
            
        except Exception as e:
            print(f"Error loading PLY file: {e}")
            self.load_default_cube()
            return False
    
    def generate_edges_from_faces(self):
        """Generate edges from face data"""
        edge_set = set()
        
        for face in self.faces:
            for i in range(len(face)):
                v1 = face[i]
                v2 = face[(i + 1) % len(face)]
                # Add edge in sorted order to avoid duplicates
                edge = tuple(sorted([v1, v2]))
                edge_set.add(edge)
        
        self.edges = list(edge_set)
    
    def normalize_model(self):
        """Normalize model to fit within a unit cube"""
        if not self.vertices:
            return
            
        vertices_array = np.array(self.vertices)
        
        # Find bounding box
        min_coords = vertices_array.min(axis=0)
        max_coords = vertices_array.max(axis=0)
        
        # Center the model
        center = (min_coords + max_coords) / 2
        vertices_array -= center
        
        # Scale to fit in unit cube
        max_extent = np.max(max_coords - min_coords)
        if max_extent > 0:
            vertices_array /= max_extent
        
        self.vertices = vertices_array.tolist()


class HandTracking3D:
    def __init__(self, width=1280, height=480):
        self.width = width
        self.height = height
        
        # Initialize 3D model
        self.model = Model3D()
        self.model.load_default_cube()
        
        pygame.init()
        self.display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Hand Tracking - Press 'L' to load model, 'R' to reset to cube")
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.webcam_surface = pygame.Surface((640, 480))
        
        # Object transformation properties
        self.cube_pos = [0, 0, -5]
        self.selected = False
        self.initial_hand_pos = None
        self.initial_cube_pos = None
        self.cube_rotation = [0, 0, 0]
        self.cube_scale = [1.0, 1.0, 1.0]
        self.selected_mode = 'position'
        self.initial_rotation = None
        self.initial_scale = None
        self.previous_scale_distance = None
        self.base_scale = 1.0
        
        self.setup_gl()

    def setup_gl(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width/2/self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0.2, 0.2, 0.2, 1)

    def load_model_dialog(self):
        """Open file dialog to load 3D model"""
        def file_dialog():
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            filetypes = [
                ('3D Model files', '*.obj *.ply'),
                ('OBJ files', '*.obj'),
                ('PLY files', '*.ply'),
                ('All files', '*.*')
            ]
            
            filepath = filedialog.askopenfilename(
                title="Select 3D Model File",
                filetypes=filetypes
            )
            
            if filepath:
                self.load_model_file(filepath)
            
            root.destroy()
        
        # Run file dialog in separate thread to avoid blocking
        thread = threading.Thread(target=file_dialog)
        thread.daemon = True
        thread.start()

    def load_model_file(self, filepath):
        """Load 3D model from file"""
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext == '.obj':
            success = self.model.load_obj_file(filepath)
        elif file_ext == '.ply':
            success = self.model.load_ply_file(filepath)
        else:
            print(f"Unsupported file format: {file_ext}")
            return False
        
        if success:
            print(f"Successfully loaded: {self.model.model_name}")
        else:
            print("Failed to load model, using default cube")
        
        return success

    def reset_to_cube(self):
        """Reset to default cube"""
        self.model.load_default_cube()
        self.cube_pos = [0, 0, -5]
        self.cube_rotation = [0, 0, 0]
        self.cube_scale = [1.0, 1.0, 1.0]
        print("Reset to default cube")

    def check_three_finger_pinch(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        
        thumb_index_dist = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 +
            (thumb_tip.y - index_tip.y)**2 +
            (thumb_tip.z - index_tip.z)**2
        )
        
        thumb_middle_dist = np.sqrt(
            (thumb_tip.x - middle_tip.x)**2 +
            (thumb_tip.y - middle_tip.y)**2 +
            (thumb_tip.z - middle_tip.z)**2
        )
        
        index_middle_dist = np.sqrt(
            (index_tip.x - middle_tip.x)**2 +
            (index_tip.y - middle_tip.y)**2 +
            (index_tip.z - middle_tip.z)**2
        )
        
        threshold = 0.1
        return all(dist < threshold for dist in [thumb_index_dist, thumb_middle_dist, index_middle_dist])

    def check_index_pinch(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 +
            (thumb_tip.y - index_tip.y)**2 +
            (thumb_tip.z - index_tip.z)**2
        )
        
        return distance < 0.1

    def get_hand_position(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[8]
        return np.array([
            (index_tip.x - 0.5) * 2,
            -(index_tip.y - 0.5) * 2,
            index_tip.z
        ])

    def calculate_scale_from_hands(self, hand_landmarks1, hand_landmarks2):
        index1 = hand_landmarks1.landmark[8]
        index2 = hand_landmarks2.landmark[8]
        
        current_distance = np.sqrt(
            (index1.x - index2.x)**2 +
            (index1.y - index2.y)**2
        )
        
        if self.previous_scale_distance is None:
            self.previous_scale_distance = current_distance
            self.base_scale = self.cube_scale[0]
            return 1.0
        
        scale_change = (current_distance / self.previous_scale_distance)
        scale_change = 1.0 + (scale_change - 1.0)
        self.previous_scale_distance = current_distance
        
        return scale_change

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return False

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        self.draw_hand_tracking(frame, results)

        if results.multi_hand_landmarks:
            primary_hand = results.multi_hand_landmarks[0]
            current_hand_pos = self.get_hand_position(primary_hand)

            # Three finger pinch for rotation
            if self.check_three_finger_pinch(primary_hand):
                if not self.selected or self.selected_mode != 'rotation':
                    self.selected = True
                    self.selected_mode = 'rotation'
                    self.initial_hand_pos = current_hand_pos
                    self.initial_rotation = np.array(self.cube_rotation)
                else:
                    delta = current_hand_pos - self.initial_hand_pos
                    self.cube_rotation[1] = self.initial_rotation[1] + delta[0] * 180
                    self.cube_rotation[0] = self.initial_rotation[0] + delta[1] * 180

            # Single hand position control
            elif self.check_index_pinch(primary_hand) and len(results.multi_hand_landmarks) == 1:
                if not self.selected or self.selected_mode != 'position':
                    self.selected = True
                    self.selected_mode = 'position'
                    self.initial_hand_pos = current_hand_pos
                    self.initial_cube_pos = np.array(self.cube_pos)
                else:
                    delta = current_hand_pos - self.initial_hand_pos
                    self.cube_pos = self.initial_cube_pos + delta * 5

            # Two-handed scaling
            if len(results.multi_hand_landmarks) == 2:
                hand1 = results.multi_hand_landmarks[0]
                hand2 = results.multi_hand_landmarks[1]
                
                if self.check_index_pinch(hand1) and self.check_index_pinch(hand2):
                    if self.selected_mode != 'scale':
                        self.selected = True
                        self.selected_mode = 'scale'
                        self.previous_scale_distance = None
                    
                    scale_factor = self.calculate_scale_from_hands(hand1, hand2)
                    new_scale = np.array(self.cube_scale) * scale_factor
                    if all(0.1 <= s <= 5.0 for s in new_scale):
                        self.cube_scale = new_scale.tolist()
            
            elif self.selected_mode == 'scale':
                self.selected = False
                self.selected_mode = 'none'
                self.previous_scale_distance = None

            # Reset if no gestures are active
            if not any([
                self.check_three_finger_pinch(primary_hand),
                (len(results.multi_hand_landmarks) == 1 and self.check_index_pinch(primary_hand)),
                (len(results.multi_hand_landmarks) == 2 and 
                 self.check_index_pinch(results.multi_hand_landmarks[0]) and 
                 self.check_index_pinch(results.multi_hand_landmarks[1]))
            ]):
                self.selected = False
                self.selected_mode = 'none'

        # Rendering
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.flip(frame, True, True)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw webcam feed
        glViewport(0, 0, self.width//2, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1, 0, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, frame.get_width(), frame.get_height(),
                    0, GL_RGB, GL_UNSIGNED_BYTE, pygame.image.tostring(frame, 'RGB', True))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(1, 0)
        glTexCoord2f(1, 0); glVertex2f(1, 1)
        glTexCoord2f(0, 0); glVertex2f(0, 1)
        glEnd()

        glDeleteTextures([texture_id])
        glDisable(GL_TEXTURE_2D)

        # Draw 3D scene
        glViewport(self.width//2, 0, self.width//2, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width/2/self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.draw_3d_model()
        pygame.display.flip()
        
        return True

    def draw_3d_model(self):
        """Draw the loaded 3D model"""
        if not self.model.has_model:
            return
            
        glLoadIdentity()
        glTranslatef(self.cube_pos[0], self.cube_pos[1], self.cube_pos[2])

        # Apply rotations
        glRotatef(self.cube_rotation[0], 1, 0, 0)
        glRotatef(self.cube_rotation[1], 0, 1, 0)
        glRotatef(self.cube_rotation[2], 0, 0, 1)
        
        # Apply scaling
        glScalef(self.cube_scale[0], self.cube_scale[1], self.cube_scale[2])
        
        # Draw edges (wireframe)
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for edge in self.model.edges:
            if len(edge) >= 2 and edge[0] < len(self.model.vertices) and edge[1] < len(self.model.vertices):
                v1 = self.model.vertices[edge[0]]
                v2 = self.model.vertices[edge[1]]
                glVertex3f(v1[0], v1[1], v1[2])
                glVertex3f(v2[0], v2[1], v2[2])
        glEnd()

        # Draw faces
        if self.selected:
            glColor4f(1.0, 0.0, 0.0, 0.5)  # Red when selected
        else:
            glColor4f(0.0, 1.0, 0.0, 0.5)  # Green when not selected

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for face in self.model.faces:
            if len(face) >= 3:  # Valid face needs at least 3 vertices
                # Draw triangulated faces
                if len(face) == 3:  # Triangle
                    glBegin(GL_TRIANGLES)
                    for vertex_idx in face:
                        if vertex_idx < len(self.model.vertices):
                            v = self.model.vertices[vertex_idx]
                            glVertex3f(v[0], v[1], v[2])
                    glEnd()
                elif len(face) == 4:  # Quad
                    glBegin(GL_QUADS)
                    for vertex_idx in face:
                        if vertex_idx < len(self.model.vertices):
                            v = self.model.vertices[vertex_idx]
                            glVertex3f(v[0], v[1], v[2])
                    glEnd()
                else:  # Polygon with more than 4 vertices - triangulate
                    glBegin(GL_TRIANGLE_FAN)
                    for vertex_idx in face:
                        if vertex_idx < len(self.model.vertices):
                            v = self.model.vertices[vertex_idx]
                            glVertex3f(v[0], v[1], v[2])
                    glEnd()
        
        glDisable(GL_BLEND)

    def draw_hand_tracking(self, frame, results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255,255,255), thickness=2)
                )
        
        # Draw UI information
        cv2.putText(frame, f"Model: {self.model.model_name}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Mode: {self.selected_mode}", 
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Scale: {self.cube_scale[0]:.2f}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, "Press 'L' to load model", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        cv2.putText(frame, "Press 'R' to reset to cube", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        if self.selected_mode == 'scale':
            cv2.putText(frame, "Scaling Active", 
                       (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_l:  # Load model
                        self.load_model_dialog()
                    elif event.key == pygame.K_r:  # Reset to cube
                        self.reset_to_cube()

            if not self.update():
                break

        self.cap.release()
        pygame.quit()

if __name__ == "__main__":
    print("3D Hand Tracking with Custom Models")
    print("Controls:")
    print("- Three finger pinch: Rotate object")
    print("- Index finger pinch (one hand): Move object")
    print("- Index finger pinch (both hands): Scale object")
    print("- Press 'L' to load a 3D model file")
    print("- Press 'R' to reset to default cube")
    print("- Press 'ESC' to exit")
    print()
    print("Supported formats: OBJ, PLY")
    
    app = HandTracking3D()
    app.run()