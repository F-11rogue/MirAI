// gallery.js - Dnails por Diana Ortiz
// Clase para la Galería Circular 3D usando Three.js

export class OptimizedCircularGallery {
    constructor(containerId, items) {
        this.container = document.getElementById(containerId);
        this.items = items;
        this.filteredItems = [...items];
        this.currentIndex = 0;
        this.rotation = 0;
        this.targetRotation = 0;
        this.isDragging = false;
        this.startX = 0;
        this.autoRotate = true;
        this.rotationSpeed = 0.003;
        this.isPaused = false;
        this.soundEnabled = false;
        this.currentFilter = 'all';
        this.meshes = [];
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.init();
    }

    init() {
        // Scene setup with fog for depth
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(0xfdf2f8, 10, 50);
        
        // Camera setup
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.z = 8;
        
        // Renderer setup with performance optimizations
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        this.container.appendChild(this.renderer.domElement);
        
        // Enhanced lighting
        this.setupLighting();
        
        // Create carousel with optimizations
        this.createCarousel();
        
        // Add particle system
        this.createParticles();
        
        // Event listeners
        this.addEventListeners();
        
        // Start animation with RAF optimization
        this.animate();
        
        // Hide loader with animation
        setTimeout(() => {
            if (typeof gsap !== 'undefined') {
                gsap.to('#loader', {
                    opacity: 0,
                    duration: 0.5,
                    onComplete: () => {
                        const loader = document.getElementById('loader');
                        if (loader) loader.style.display = 'none';
                    }
                });
            } else {
                const loader = document.getElementById('loader');
                if (loader) loader.style.display = 'none';
            }
        }, 1000);
    }

    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Rim lights for depth
        const rimLight1 = new THREE.DirectionalLight(0xc5a065, 0.3);
        rimLight1.position.set(-5, 0, -5);
        this.scene.add(rimLight1);
        
        const rimLight2 = new THREE.DirectionalLight(0xdcb4b4, 0.2);
        rimLight2.position.set(5, 0, -5);
        this.scene.add(rimLight2);
        
        // Point light for dynamic feel
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 100);
        pointLight.position.set(0, 5, 0);
        this.scene.add(pointLight);
    }

    createCarousel() {
        this.carousel = new THREE.Group();
        this.scene.add(this.carousel);
        
        const radius = 5;
        const count = this.filteredItems.length;
        
        // Create geometry once and reuse
        const geometry = new THREE.PlaneGeometry(2.5, 3.5);
        
        this.filteredItems.forEach((item, index) => {
            // Load texture with caching
            const textureLoader = new THREE.TextureLoader();
            const texture = textureLoader.load(item.image);
            texture.encoding = THREE.sRGBEncoding;
            texture.generateMipmaps = false;
            texture.minFilter = THREE.LinearFilter;
            texture.magFilter = THREE.LinearFilter;
            
            // Enhanced material with better properties
            const material = new THREE.MeshStandardMaterial({
                map: texture,
                side: THREE.DoubleSide,
                metalness: 0.1,
                roughness: 0.4,
                envMapIntensity: 0.5
            });
            
            // Create mesh
            const mesh = new THREE.Mesh(geometry, material);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            
            // Position in circle
            const angle = (index / count) * Math.PI * 2;
            mesh.position.x = Math.sin(angle) * radius;
            mesh.position.z = Math.cos(angle) * radius;
            mesh.rotation.y = -angle;
            
            // Add to carousel
            this.carousel.add(mesh);
            
            // Store reference
            mesh.userData = { 
                index, 
                title: item.text,
                category: item.category || 'all',
                originalIndex: item.originalIndex || index
            };
            
            this.meshes.push(mesh);
        });
    }

    createParticles() {
        const particlesGeometry = new THREE.BufferGeometry();
        const particlesCount = 100;
        const posArray = new Float32Array(particlesCount * 3);
        
        for(let i = 0; i < particlesCount * 3; i++) {
            posArray[i] = (Math.random() - 0.5) * 20;
        }
        
        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        
        const particlesMaterial = new THREE.PointsMaterial({
            size: 0.02,
            color: 0xc5a065,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });
        
        this.particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
        this.scene.add(this.particlesMesh);
    }

    addEventListeners() {
        // Mouse events with optimization
        this.container.addEventListener('mousedown', this.onMouseDown.bind(this));
        window.addEventListener('mousemove', this.onMouseMove.bind(this));
        window.addEventListener('mouseup', this.onMouseUp.bind(this));
        
        // Touch events
        this.container.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: false });
        window.addEventListener('touchmove', this.onTouchMove.bind(this), { passive: false });
        window.addEventListener('touchend', this.onTouchEnd.bind(this));
        
        // Double click for fullscreen
        this.container.addEventListener('dblclick', this.onDoubleClick.bind(this));
        
        // Navigation buttons
        const prevBtn = document.getElementById('prevBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', (event) => {
                this.navigate(-1);
                this.createClickEffect(event.clientX, event.clientY);
            });
        }
        
        const nextBtn = document.getElementById('nextBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', (event) => {
                this.navigate(1);
                this.createClickEffect(event.clientX, event.clientY);
            });
        }
        
        // Control buttons
        const pauseBtn = document.getElementById('pauseBtn');
        if (pauseBtn) pauseBtn.addEventListener('click', this.togglePause.bind(this));
        
        const speedBtn = document.getElementById('speedBtn');
        if (speedBtn) speedBtn.addEventListener('click', this.changeSpeed.bind(this));
        
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        if (fullscreenBtn) fullscreenBtn.addEventListener('click', this.toggleFullscreen.bind(this));
        
        const soundBtn = document.getElementById('soundBtn');
        if (soundBtn) soundBtn.addEventListener('click', this.toggleSound.bind(this));
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', this.filterItems.bind(this));
        });
        
        // Keyboard navigation
        window.addEventListener('keydown', this.onKeyDown.bind(this));
        
        // Window resize with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(this.onWindowResize.bind(this), 250);
        });
        
        // Fullscreen modal
        const fullscreenClose = document.getElementById('fullscreenClose');
        if (fullscreenClose) fullscreenClose.addEventListener('click', this.closeFullscreen.bind(this));
        
        const fullscreenModal = document.getElementById('fullscreenModal');
        if (fullscreenModal) {
            fullscreenModal.addEventListener('click', (e) => {
                if (e.target.id === 'fullscreenModal') {
                    this.closeFullscreen();
                }
            });
        }
    }

    onMouseDown(event) {
        this.isDragging = true;
        this.autoRotate = false;
        this.startX = event.clientX;
        this.container.classList.add('grabbing');
        this.container.style.cursor = 'grabbing';
    }

    onMouseMove(event) {
        if (!this.isDragging) return;
        
        const deltaX = event.clientX - this.startX;
        this.targetRotation += deltaX * 0.01;
        this.startX = event.clientX;
        
        // Update mouse position for raycasting
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    onMouseUp() {
        this.isDragging = false;
        this.container.classList.remove('grabbing');
        this.container.style.cursor = 'grab';
        
        setTimeout(() => {
            if (!this.isPaused) {
                this.autoRotate = true;
            }
        }, 3000);
    }

    onTouchStart(event) {
        // event.preventDefault(); // Removed to allow scrolling if needed, or handle carefully
        this.isDragging = true;
        this.autoRotate = false;
        this.startX = event.touches[0].clientX;
    }

    onTouchMove(event) {
        if (!this.isDragging) return;
        // event.preventDefault();
        
        const deltaX = event.touches[0].clientX - this.startX;
        this.targetRotation += deltaX * 0.01;
        this.startX = event.touches[0].clientX;
    }

    onTouchEnd() {
        this.isDragging = false;
        setTimeout(() => {
            if (!this.isPaused) {
                this.autoRotate = true;
            }
        }, 3000);
    }

    onDoubleClick(event) {
        const rect = this.container.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
        const intersects = this.raycaster.intersectObjects(this.meshes);
        
        if (intersects.length > 0) {
            const clickedMesh = intersects[0].object;
            const item = this.items[clickedMesh.userData.originalIndex];
            this.openFullscreen(item.image);
        }
    }

    onKeyDown(event) {
        switch(event.key) {
            case 'ArrowLeft':
                this.navigate(-1);
                break;
            case 'ArrowRight':
                this.navigate(1);
                break;
            case ' ':
                event.preventDefault();
                this.togglePause();
                break;
            case 'f':
                this.toggleFullscreen();
                break;
        }
    }

    navigate(direction) {
        this.autoRotate = false;
        const angleStep = (Math.PI * 2) / this.filteredItems.length;
        this.targetRotation += direction * angleStep;
        
        setTimeout(() => {
            if (!this.isPaused) {
                this.autoRotate = true;
            }
        }, 3000);
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        this.autoRotate = !this.isPaused;
        const btn = document.getElementById('pauseBtn');
        if (btn) btn.innerHTML = this.isPaused ? '<i class="fas fa-play"></i>' : '<i class="fas fa-pause"></i>';
    }

    changeSpeed() {
        const speeds = [0.001, 0.003, 0.005, 0.008];
        const currentIndex = speeds.indexOf(this.rotationSpeed);
        this.rotationSpeed = speeds[(currentIndex + 1) % speeds.length];
        
        // Visual feedback
        const btn = document.getElementById('speedBtn');
        if (btn && typeof gsap !== 'undefined') {
            gsap.to(btn, {
                scale: 1.2,
                duration: 0.2,
                yoyo: true,
                repeat: 1
            });
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen();
        }
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        const btn = document.getElementById('soundBtn');
        if (btn) {
            btn.innerHTML = this.soundEnabled ? 
                '<i class="fas fa-volume-up"></i>' : 
                '<i class="fas fa-volume-mute"></i>';
        }
    }

    filterItems(event) {
        const filter = event.target.dataset.filter;
        this.currentFilter = filter;
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Filter items
        if (filter === 'all') {
            this.filteredItems = [...this.items];
        } else {
            this.filteredItems = this.items.filter(item => 
                item.category === filter
            );
        }
        
        // Rebuild carousel
        this.rebuildCarousel();
    }

    rebuildCarousel() {
        // Clear existing meshes
        this.meshes.forEach(mesh => {
            this.carousel.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        });
        this.meshes = [];
        
        // Recreate with filtered items
        this.createCarousel();
    }

    openFullscreen(imageSrc) {
        const modal = document.getElementById('fullscreenModal');
        const img = document.getElementById('fullscreenImage');
        if (modal && img) {
            img.src = imageSrc;
            modal.classList.add('active');
        }
    }

    closeFullscreen() {
        const modal = document.getElementById('fullscreenModal');
        if (modal) modal.classList.remove('active');
    }

    createClickEffect(x, y) {
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            particle.style.animation = `particle-float ${1 + Math.random()}s ease-out forwards`;
            particle.style.animationDelay = `${Math.random() * 0.2}s`;
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 2000);
        }
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    updateGalleryInfo() {
        const info = document.getElementById('galleryInfo');
        const progressBar = document.getElementById('progressBar');
        
        if (!info || !progressBar) return;

        // Calculate closest index
        const normalizedRotation = ((this.rotation % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
        const angleStep = (Math.PI * 2) / this.filteredItems.length;
        const closestIndex = Math.round(normalizedRotation / angleStep) % this.filteredItems.length;
        
        if (this.filteredItems[closestIndex]) {
            info.textContent = this.filteredItems[closestIndex].text;
            info.classList.add('show');
            
            // Update progress bar
            const progress = ((closestIndex + 1) / this.filteredItems.length) * 100;
            progressBar.style.width = progress + '%';
        }
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        // Auto rotation with pause support
        if (this.autoRotate && !this.isDragging && !this.isPaused) {
            this.targetRotation += this.rotationSpeed;
        }
        
        // Smooth rotation with easing
        this.rotation += (this.targetRotation - this.rotation) * 0.08;
        this.carousel.rotation.y = this.rotation;
        
        // Animate particles
        if (this.particlesMesh) {
            this.particlesMesh.rotation.y += 0.0005;
            this.particlesMesh.rotation.x += 0.0002;
        }
        
        // Update info
        this.updateGalleryInfo();
        
        // Render with optimizations
        this.renderer.render(this.scene, this.camera);
    }
}
