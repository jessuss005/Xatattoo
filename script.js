class StencilGenerator {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const edgeThreshold = document.getElementById('edgeThreshold');
        const thresholdValue = document.getElementById('thresholdValue');

        // Área de upload
        uploadArea.addEventListener('click', () => imageInput.click());
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Input de archivo
        imageInput.addEventListener('change', (e) => this.handleImageSelect(e));

        // Control deslizante
        edgeThreshold.addEventListener('input', (e) => {
            thresholdValue.textContent = e.target.value;
        });

        // Botones
        generateBtn.addEventListener('click', () => this.generateStencil());
        downloadBtn.addEventListener('click', () => this.downloadStencil());
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.style.background = '#eef1ff';
        e.currentTarget.style.borderColor = '#764ba2';
    }

    handleDrop(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            this.processImageFile(files[0]);
        }
    }

    handleImageSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processImageFile(file);
        }
    }

    processImageFile(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const originalImage = document.getElementById('originalImage');
            originalImage.src = e.target.result;
            
            // Mostrar controles y área de resultados
            document.getElementById('controls').style.display = 'block';
            document.getElementById('results').style.display = 'block';
            
            // Scroll a los resultados
            document.getElementById('results').scrollIntoView({ 
                behavior: 'smooth' 
            });
        };
        
        reader.readAsDataURL(file);
    }

    async generateStencil() {
        const originalImage = document.getElementById('originalImage');
        const threshold = document.getElementById('edgeThreshold').value;
        
        if (!originalImage.src || originalImage.src === '#') {
            alert('Por favor, selecciona una imagen primero.');
            return;
        }

        // Mostrar loading
        document.getElementById('loading').style.display = 'block';

        try {
            // Convertir imagen a Blob para enviar al servidor
            const response = await fetch(originalImage.src);
            const blob = await response.blob();
            
            const formData = new FormData();
            formData.append('image', blob);
            formData.append('threshold', threshold);

            const serverResponse = await fetch('/generate-stencil', {
                method: 'POST',
                body: formData
            });

            if (!serverResponse.ok) {
                throw new Error('Error del servidor');
            }

            const stencilBlob = await serverResponse.blob();
            const stencilUrl = URL.createObjectURL(stencilBlob);
            
            document.getElementById('stencilImage').src = stencilUrl;
            
            // Guardar URL para descarga
            this.currentStencilUrl = stencilUrl;

        } catch (error) {
            console.error('Error:', error);
            alert('Error al generar el esténcil. Asegúrate de que el servidor esté funcionando.');
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    }

    downloadStencil() {
        if (!this.currentStencilUrl) {
            alert('Primero genera un esténcil.');
            return;
        }

        const link = document.createElement('a');
        link.href = this.currentStencilUrl;
        link.download = 'stencil-tatuaje.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    new StencilGenerator();
});