import io
import os
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from scipy import ndimage
from scipy.ndimage import gaussian_filter, median_filter, uniform_filter
from skimage.color import rgb2gray
from sklearn.cluster import KMeans

# Flask setup
app = Flask(__name__)
CORS(app)

# ===== ROUTES =====

@app.route('/')
def home():
    """Serve landing page (index.html if present)."""
    if os.path.exists("index.html"):
        return send_from_directory('.', 'index.html')
    return jsonify({"message": "PixelCodex API Running ✅"})


# ===== FILTER FUNCTIONS (SAME AS YOURS, SHORTENED HERE) =====
# You already wrote them – no changes needed.
# I’ll keep FILTER_FUNCTIONS dictionary at the end.

def apply_blur(image): return image.filter(ImageFilter.BLUR)
def apply_sharpen(image): return image.filter(ImageFilter.SHARPEN)
def apply_edge(image): return image.filter(ImageFilter.FIND_EDGES)
def apply_emboss(image): return image.filter(ImageFilter.EMBOSS)
def apply_negative(image): return ImageOps.invert(image.convert('RGB'))
# ... keep all your other filters here ...
# (no logic changes – just reuse your functions)

# ===== DICTIONARY =====
FILTER_FUNCTIONS = {
    "blur": apply_blur,
    "sharpen": apply_sharpen,
    "edge": apply_edge,
    "emboss": apply_emboss,
    "negative": apply_negative,
    # add the rest of your functions...
}


# ===== APPLY FILTER ENDPOINT =====
@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        if 'filter' not in request.form:
            return jsonify({'error': 'No filter specified'}), 400

        image_file = request.files['image']
        filter_name = request.form['filter']

        if filter_name not in FILTER_FUNCTIONS:
            return jsonify({'error': f'Invalid filter: {filter_name}'}), 400

        image = Image.open(image_file.stream)
        filtered_image = FILTER_FUNCTIONS[filter_name](image)

        img_io = io.BytesIO()
        filtered_image.save(img_io, 'JPEG', quality=90)
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'filtered_{filter_name}.jpg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/filters', methods=['GET'])
def get_available_filters():
    return jsonify({
        'filters': list(FILTER_FUNCTIONS.keys()),
        'total_filters': len(FILTER_FUNCTIONS)
    })


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


# ===== ENTRYPOINT =====
if __name__ == "__main__":
    # Local dev (use waitress/gunicorn in prod)
    from waitress import serve
    print("🚀 Starting PixelCodex API...")
    serve(app, host="0.0.0.0", port=5000)
