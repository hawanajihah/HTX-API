# import modules

from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, UnidentifiedImageError
import io
import logging
import time
from datetime import datetime
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# create flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app) # create database object

# create columns for SQL database
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    status = db.Column(db.String(20), default='processing')  # processing status
    processing_time = db.Column(db.Float, default=0.0) # processing time
    processed_at = db.Column(db.String(25), default=None)  # processing timestamp

# define size of small and medium thumbnails respectively
thumbnail_size = {
    "small": (150, 150),
    "medium": (300, 300)
}

# filtering - only supported formats are allowed for image uploads
allowed_extensions = {"jpg", "jpeg", "png"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# load BLIP processing model
processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = AutoModelForImageTextToText.from_pretrained("Salesforce/blip-image-captioning-base")

# extract metadata from an image
def extract_metadata(image):
    """Extract metadata from an image."""
    metadata = {
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "size_bytes": len(image.tobytes())
    }
    return metadata

# generate thumbnails - small and large
def generate_thumbnail(image, size):
    """Generate a thumbnail of the given size."""
    img_copy = image.copy()
    img_copy.thumbnail(size)
    img_io = io.BytesIO()
    img_copy.save(img_io, format='PNG')
    return img_io.getvalue()

# generate caption using AI
def generate_caption(image):
    """Generate a caption for an image using BLIP."""
    inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

# accepts image uploads - only supports PNG and JPEG images
@app.route('/api/images', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded."}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid images. Only JPEG and PNG files are allowed."}), 400
    
    try:
        # attempt to open the image and check for corrupt data
        image = Image.open(file)
        image.verify()  # this will check if the image is broken or corrupted

        # reopen the image after verification 
        file.seek(0)  # reset file pointer before reopening
        image = Image.open(file)

    except (OSError, UnidentifiedImageError) as e:
        logging.error(f"Error while processing the image: {e}")
        return jsonify({"error": "Broken or corrupted image file."}), 400 
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred while processing the image."}), 500 # will not store broken or corrupted files into database

    # save initial record with processing status
    upload = Upload(filename=file.filename, status='processing')
    db.session.add(upload)
    db.session.commit()

    logging.info(f"Processing image {upload.id}: {file.filename}")
    start_time = time.time()

    # convert image to binary for storage
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    img_data = img_io.getvalue()

    # update record with completed processing
    upload.data = img_data
    upload.status = 'processed'
    upload.processing_time = time.time() - start_time
    upload.processed_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    db.session.commit()

    logging.info(f"Finished processing image {upload.id}: {file.filename}")
    return jsonify({"image_id": upload.id, "status": upload.status}), 202

# list processing and processed images
@app.route('/api/images', methods=['GET'])
def list_images():
    """List all processed or processing images."""
    
    images = Upload.query.all()
    result = [{
        "id": image.id,
        "filename": image.filename,
        "status": image.status
    } for image in images]

    return jsonify(result)

# get details for specific image
@app.route('/api/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    """Get specific image details, including metadata and analysis."""
    upload = Upload.query.get(image_id)
    if not upload:
        return jsonify({"error": "Image not found"}), 404
    
    try:
        image = Image.open(io.BytesIO(upload.data))
    except UnidentifiedImageError:
        logging.error("Uploaded file failed to process properly")
        return jsonify({"error": "Processing failure"}), 400

    metadata = extract_metadata(image)
    caption = generate_caption(image)

    # error message
    error = None
    if upload.status == "processing":
        error = True

    return jsonify({
        "status": upload.status,
        "data": {
            "id": upload.id,
            "filename": upload.filename,
            "metadata": metadata,
            "processed_at": upload.processed_at,
            "caption": caption,
        },
        "thumbnails": {
            size_label: f"http://localhost:8000/api/images/{image_id}/thumbnails/{size_label}"
            for size_label in thumbnail_size.keys()
        },
        "error": error
    })

# gets either small or medium thumbnail
@app.route('/api/images/<int:image_id>/thumbnails/<string:size>', methods=['GET'])
def get_thumbnail(image_id, size):
    if size not in thumbnail_size:
        return jsonify({"error": "Invalid thumbnail size. Choose 'small' or 'medium'."}), 400
    
    upload = Upload.query.get(image_id)
    if not upload:
        return jsonify({"error": "Image not found"}), 404
    
    try:
        image = Image.open(io.BytesIO(upload.data))
    except UnidentifiedImageError:
        logging.error("Uploaded file failed to process properly")
        return jsonify({"error": "Processing failure"}), 400
    
    img_copy = image.copy()
    img_copy.thumbnail(thumbnail_size[size])

    img_io = io.BytesIO()
    img_copy.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

# reveal statistics for the API
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return processing statistics, including success/failure rates and average processing time."""
    total_images = Upload.query.count()
    processed_images = Upload.query.filter_by(status='processed').count()
    failed_images = total_images - processed_images
    avg_processing_time = db.session.query(db.func.avg(Upload.processing_time)).scalar()
    
    return jsonify({
        "images": {
            "total_images": total_images,
            "processed_images": processed_images,
            "failed_images": failed_images,
        },
        "average_processing_time": f"{round(avg_processing_time, 2)}s (to 2 dp)",
        "success_failures_rate": {
            "success_rate": f"{round((processed_images / total_images)*100, 2)}%",
            "failure_rate": f"{round((failed_images / total_images)*100, 2)}%"
        }
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)