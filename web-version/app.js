class HandTrackingCubeApp {
    constructor() {
        // Configuration from provided data
        this.config = {
            gestures: {
                three_finger_pinch: {
                    fingers: ["thumb", "index", "middle"],
                    threshold: 0.1,
                    mode: "rotation"
                },
                two_finger_pinch: {
                    fingers: ["thumb", "index"], 
                    threshold: 0.1,
                    mode: "position_or_scale"
                }
            },
            cube_properties: {
                initial_position: [0, 0, -5],
                initial_rotation: [0, 0, 0],
                initial_scale: [1, 1, 1],
                idle_color: 0x00ff00,
                selected_color: 0xff0000
            },
            camera_config: {
                width: 640,
                height: 480,
                video_constraints: {
                    video: { width: 640, height: 480 },
                    audio: false
                }
            },
            mediapipe_config: {
                max_hands: 2,
                detection_confidence: 0.7,
                tracking_confidence: 0.5
            }
        };

        // State management
        this.currentMode = 'idle';
        this.handsData = [];
        this.previousGestureData = null;
        this.cubeTransform = {
            position: [...this.config.cube_properties.initial_position],
            rotation: [...this.config.cube_properties.initial_rotation],
            scale: this.config.cube_properties.initial_scale[0]
        };

        // Initialize components
        this.initializeElements();
        this.init();
    }

    async init() {
        try {
            this.setupThreeJS();
            await this.setupMediaPipe();
            this.setupEventListeners();
            await this.startCamera();
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError();
        }
    }

    initializeElements() {
        this.videoElement = document.getElementById('videoElement');
        this.canvasElement = document.getElementById('canvasElement');
        this.sceneContainer = document.getElementById('sceneContainer');
        this.loadingMessage = document.getElementById('loadingMessage');
        this.errorMessage = document.getElementById('errorMessage');
        this.modeStatus = document.getElementById('modeStatus');
        this.handsStatus = document.getElementById('handsStatus');
        this.positionDisplay = document.getElementById('positionDisplay');
        this.rotationDisplay = document.getElementById('rotationDisplay');
        this.scaleDisplay = document.getElementById('scaleDisplay');
        this.retryButton = document.getElementById('retryButton');
        this.resetButton = document.getElementById('resetButton');
    }

    setupThreeJS() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x222222);
        
        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        this.camera.position.set(0, 0, 2);
        
        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // Add renderer to container
        this.sceneContainer.appendChild(this.renderer.domElement);

        // Create cube geometry and material
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshLambertMaterial({ 
            color: this.config.cube_properties.idle_color
        });
        this.cube = new THREE.Mesh(geometry, material);
        
        // Set initial cube position
        this.cube.position.set(...this.config.cube_properties.initial_position);
        this.scene.add(this.cube);

        // Add lighting for better visibility
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        this.scene.add(directionalLight);

        // Handle initial resize
        this.handleResize();
        
        // Start render loop
        this.animate();

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    async setupMediaPipe() {
        return new Promise((resolve, reject) => {
            try {
                this.hands = new Hands({
                    locateFile: (file) => {
                        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                    }
                });

                this.hands.setOptions({
                    maxNumHands: this.config.mediapipe_config.max_hands,
                    modelComplexity: 1,
                    minDetectionConfidence: this.config.mediapipe_config.detection_confidence,
                    minTrackingConfidence: this.config.mediapipe_config.tracking_confidence
                });

                this.hands.onResults((results) => this.onHandsResults(results));
                
                // Initialize canvas context
                this.canvasCtx = this.canvasElement.getContext('2d');
                
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    setupEventListeners() {
        this.retryButton.addEventListener('click', () => this.startCamera());
        this.resetButton.addEventListener('click', () => this.resetCube());
    }

    async startCamera() {
        try {
            this.hideError();
            this.showLoading();

            // Request camera permission
            const stream = await navigator.mediaDevices.getUserMedia(
                this.config.camera_config.video_constraints
            );
            
            this.videoElement.srcObject = stream;
            
            // Wait for video to load
            await new Promise((resolve) => {
                this.videoElement.addEventListener('loadedmetadata', resolve, { once: true });
            });

            // Setup canvas and start tracking
            this.setupCanvasSize();
            this.hideLoading();
            this.startHandTracking();
            
        } catch (error) {
            console.error('Camera access error:', error);
            this.showError();
        }
    }

    setupCanvasSize() {
        // Set canvas size to match video element
        const rect = this.videoElement.getBoundingClientRect();
        this.canvasElement.width = this.videoElement.videoWidth || rect.width;
        this.canvasElement.height = this.videoElement.videoHeight || rect.height;
        this.canvasElement.style.width = rect.width + 'px';
        this.canvasElement.style.height = rect.height + 'px';
    }

    startHandTracking() {
        if (typeof Camera === 'undefined') {
            console.error('MediaPipe Camera not loaded');
            this.showError();
            return;
        }

        this.camera_mp = new Camera(this.videoElement, {
            onFrame: async () => {
                await this.hands.send({ image: this.videoElement });
            },
            width: this.config.camera_config.width,
            height: this.config.camera_config.height
        });
        
        this.camera_mp.start();
    }

    onHandsResults(results) {
        this.handsData = results.multiHandLandmarks || [];
        this.drawHandLandmarks(results);
        this.processGestures();
        this.updateUI();
    }

    drawHandLandmarks(results) {
        if (!this.canvasCtx) return;
        
        this.canvasCtx.save();
        this.canvasCtx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

        if (results.multiHandLandmarks && typeof drawConnectors !== 'undefined') {
            for (const landmarks of results.multiHandLandmarks) {
                drawConnectors(this.canvasCtx, landmarks, HAND_CONNECTIONS, {color: '#00FF00', lineWidth: 2});
                drawLandmarks(this.canvasCtx, landmarks, {color: '#FF0000', lineWidth: 2});
            }
        }
        this.canvasCtx.restore();
    }

    processGestures() {
        if (this.handsData.length === 0) {
            this.setMode('idle');
            return;
        }

        const gestureData = this.analyzeGestures();
        
        if (gestureData) {
            this.applyGestureToTransform(gestureData);
        } else {
            this.setMode('idle');
        }
    }

    analyzeGestures() {
        if (this.handsData.length === 1) {
            const hand = this.handsData[0];
            const gesture = this.detectGesture(hand);
            
            if (gesture === 'three_finger_pinch') {
                return {
                    type: 'rotation',
                    hands: [hand],
                    center: this.getHandCenter(hand)
                };
            } else if (gesture === 'two_finger_pinch') {
                return {
                    type: 'position',
                    hands: [hand],
                    center: this.getHandCenter(hand)
                };
            }
        } else if (this.handsData.length === 2) {
            const hand1 = this.handsData[0];
            const hand2 = this.handsData[1];
            
            if (this.detectGesture(hand1) === 'two_finger_pinch' && 
                this.detectGesture(hand2) === 'two_finger_pinch') {
                return {
                    type: 'scale',
                    hands: [hand1, hand2],
                    center: this.getTwoHandCenter(hand1, hand2),
                    distance: this.getHandDistance(hand1, hand2)
                };
            }
        }
        
        return null;
    }

    detectGesture(hand) {
        const thumb = hand[4];
        const index = hand[8];
        const middle = hand[12];

        // Two finger pinch (thumb + index)
        const thumbIndexDist = this.getDistance(thumb, index);
        if (thumbIndexDist < this.config.gestures.two_finger_pinch.threshold) {
            // Check if middle finger is extended (not pinching)
            const thumbMiddleDist = this.getDistance(thumb, middle);
            if (thumbMiddleDist > this.config.gestures.three_finger_pinch.threshold * 1.5) {
                return 'two_finger_pinch';
            }
        }

        // Three finger pinch (thumb + index + middle)
        const thumbMiddleDist = this.getDistance(thumb, middle);
        if (thumbIndexDist < this.config.gestures.three_finger_pinch.threshold && 
            thumbMiddleDist < this.config.gestures.three_finger_pinch.threshold) {
            return 'three_finger_pinch';
        }

        return null;
    }

    getDistance(point1, point2) {
        return Math.sqrt(
            Math.pow(point1.x - point2.x, 2) + 
            Math.pow(point1.y - point2.y, 2) + 
            Math.pow(point1.z - point2.z, 2)
        );
    }

    getHandCenter(hand) {
        const wrist = hand[0];
        return { x: wrist.x, y: wrist.y, z: wrist.z };
    }

    getTwoHandCenter(hand1, hand2) {
        const center1 = this.getHandCenter(hand1);
        const center2 = this.getHandCenter(hand2);
        return {
            x: (center1.x + center2.x) / 2,
            y: (center1.y + center2.y) / 2,
            z: (center1.z + center2.z) / 2
        };
    }

    getHandDistance(hand1, hand2) {
        const center1 = this.getHandCenter(hand1);
        const center2 = this.getHandCenter(hand2);
        return this.getDistance(center1, center2);
    }

    applyGestureToTransform(gestureData) {
        const sensitivity = {
            position: 5,
            rotation: 3,
            scale: 2
        };

        switch (gestureData.type) {
            case 'position':
                this.setMode('position');
                if (this.previousGestureData && this.previousGestureData.type === 'position') {
                    const deltaX = (gestureData.center.x - this.previousGestureData.center.x) * sensitivity.position;
                    const deltaY = -(gestureData.center.y - this.previousGestureData.center.y) * sensitivity.position;
                    
                    this.cubeTransform.position[0] += deltaX;
                    this.cubeTransform.position[1] += deltaY;
                }
                break;

            case 'rotation':
                this.setMode('rotation');
                if (this.previousGestureData && this.previousGestureData.type === 'rotation') {
                    const deltaX = (gestureData.center.x - this.previousGestureData.center.x) * sensitivity.rotation;
                    const deltaY = (gestureData.center.y - this.previousGestureData.center.y) * sensitivity.rotation;
                    
                    this.cubeTransform.rotation[1] += deltaX;
                    this.cubeTransform.rotation[0] += deltaY;
                }
                break;

            case 'scale':
                this.setMode('scale');
                if (this.previousGestureData && this.previousGestureData.type === 'scale') {
                    const deltaDistance = gestureData.distance - this.previousGestureData.distance;
                    const scaleChange = deltaDistance * sensitivity.scale;
                    
                    this.cubeTransform.scale = Math.max(0.1, Math.min(3, this.cubeTransform.scale + scaleChange));
                }
                break;
        }

        this.previousGestureData = gestureData;
        this.updateCubeTransform();
    }

    updateCubeTransform() {
        this.cube.position.set(...this.cubeTransform.position);
        this.cube.rotation.set(...this.cubeTransform.rotation);
        this.cube.scale.set(this.cubeTransform.scale, this.cubeTransform.scale, this.cubeTransform.scale);
    }

    setMode(mode) {
        if (this.currentMode === mode) return;
        
        this.currentMode = mode;
        
        // Update cube color
        const color = (mode === 'idle') ? 
            this.config.cube_properties.idle_color : 
            this.config.cube_properties.selected_color;
        
        this.cube.material.color.setHex(color);
        
        // Reset previous gesture data when changing modes
        if (mode === 'idle') {
            this.previousGestureData = null;
        }
    }

    resetCube() {
        this.cubeTransform = {
            position: [...this.config.cube_properties.initial_position],
            rotation: [...this.config.cube_properties.initial_rotation],
            scale: this.config.cube_properties.initial_scale[0]
        };
        this.updateCubeTransform();
        this.setMode('idle');
    }

    updateUI() {
        // Update mode status
        const modeText = {
            'idle': 'Ready',
            'position': 'Moving Position',
            'rotation': 'Rotating',
            'scale': 'Scaling'
        };
        
        this.modeStatus.textContent = modeText[this.currentMode] || 'Ready';
        this.modeStatus.className = 'status ' + (this.currentMode === 'idle' ? 'mode-idle' : 'mode-active');

        // Update hands status
        const handsCount = this.handsData.length;
        this.handsStatus.textContent = handsCount === 0 ? 'No hands detected' : 
                                      handsCount === 1 ? '1 hand detected' : 
                                      `${handsCount} hands detected`;

        // Update transform displays
        this.positionDisplay.textContent = this.cubeTransform.position.map(v => v.toFixed(1)).join(', ');
        this.rotationDisplay.textContent = this.cubeTransform.rotation.map(v => (v * 180 / Math.PI).toFixed(0) + '°').join(', ');
        this.scaleDisplay.textContent = this.cubeTransform.scale.toFixed(2);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }

    handleResize() {
        const container = this.sceneContainer;
        const rect = container.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        
        if (width > 0 && height > 0) {
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        }
        
        // Also update canvas size if video is loaded
        if (this.videoElement && this.videoElement.videoWidth > 0) {
            this.setupCanvasSize();
        }
    }

    showLoading() {
        this.loadingMessage.classList.remove('hidden');
        this.errorMessage.classList.add('hidden');
    }

    hideLoading() {
        this.loadingMessage.classList.add('hidden');
    }

    showError() {
        this.loadingMessage.classList.add('hidden');
        this.errorMessage.classList.remove('hidden');
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new HandTrackingCubeApp();
});