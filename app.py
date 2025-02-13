from flask import Flask, request, send_file, render_template
from PIL import Image
import io

app = Flask(__name__)

# Configure allowed formats
ALLOWED_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP', 'BMP']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    # Check if file was uploaded
    if 'file' not in request.files:
        return {'error': 'No file uploaded'}, 400
    
    file = request.files['file']
    target_format = request.form.get('target_format')

    # Validate inputs
    if not target_format or target_format not in ALLOWED_FORMATS:
        return {'error': 'Invalid target format'}, 400
    
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    try:
        # Open and convert image
        img = Image.open(file.stream)
        img_bytes = io.BytesIO()
        
        # Handle transparency for formats that don't support it
        if target_format in ['JPEG', 'BMP'] and img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        img.save(img_bytes, format=target_format)
        img_bytes.seek(0)

        # Determine MIME type
        mime_type = f'image/{target_format.lower()}'
        if target_format == 'JPEG':
            mime_type = 'image/jpeg'

        return send_file(
            img_bytes,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f'converted_image.{target_format.lower()}'
        )

    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)