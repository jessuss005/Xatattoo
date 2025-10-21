from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)
CORS(app)

def create_stencil_cv2(image_data, threshold=50):
    """
    Enfoque alternativo usando umbralización adaptativa - MÁS EFECTIVO
    """
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("No se pudo decodificar la imagen")
        
        # Redimensionar si es necesario
        height, width = img.shape[:2]
        if height > 1000 or width > 1000:
            scale = 1000 / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale)
        
        # 1. Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Mejorar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 3. Aplicar blur para reducir ruido
        blurred = cv2.medianBlur(gray, 5)
        
        # 4. Detección de bordes con Laplacian (alternativa a Canny)
        edges = cv2.Laplacian(blurred, cv2.CV_8U, ksize=3)
        
        # 5. Umbralización adaptativa - MÁS ROBUSTA
        # Convertir threshold de 0-100 a 0-255
        threshold_value = int(threshold * 2.55)
        _, binary = cv2.threshold(edges, threshold_value, 255, cv2.THRESH_BINARY)
        
        # 6. Operaciones morfológicas para mejorar los bordes
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 7. Invertir colores (bordes blancos sobre fondo negro)
        inverted = cv2.bitwise_not(binary)
        
        print(f"Procesamiento alternativo completado - Threshold usado: {threshold_value}")
        
        return inverted
        
    except Exception as e:
        print(f"Error en procesamiento alternativo: {str(e)}")
        raise

@app.route('/')
def serve_frontend():
    """Sirve el archivo HTML principal"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Archivo index.html no encontrado", 404

@app.route('/generate-stencil', methods=['POST'])
def generate_stencil():
    """
    Endpoint que recibe una imagen y devuelve el esténcil procesado
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        image_data = image_file.read()
        threshold = int(request.form.get('threshold', 50))
        
        # Crear el esténcil con OpenCV
        stencil_image = create_stencil_cv2(image_data, threshold)
        
        # Codificar la imagen resultante como PNG
        success, encoded_image = cv2.imencode('.png', stencil_image)
        
        if not success:
            return jsonify({'error': 'Error al codificar la imagen'}), 500
        
        # Crear un objeto BytesIO para enviar la imagen
        image_io = BytesIO(encoded_image.tobytes())
        image_io.seek(0)
        
        return send_file(
            image_io,
            mimetype='image/png',
            as_attachment=False,
            download_name='stencil.png'
        )
        
    except Exception as e:
        print(f"Error en el servidor: {str(e)}")
        return jsonify({'error': f'Error del servidor: {str(e)}'}), 500

@app.route('/style.css')
def serve_css():
    with open('style.css', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/script.js')
def serve_js():
    with open('script.js', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    print("🎨 Iniciando Generador de Esténciles para Tatuajes...")
    print("📍 La aplicación estará disponible en: http://localhost:5000")
    print("🖼️ Usando OpenCV MEJORADO para procesamiento de imágenes")
    app.run(debug=True, host='0.0.0.0', port=5000)