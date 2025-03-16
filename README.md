# HTX-API

## Project Overview
This API is an image processing pipeline designed to automatically process uploaded images, generate thumbnails, extract metadata, and provide AI-generated captions using the Salesforce BLIP Image Captioning Model. It also tracks processing time and maintains a database record for each uploaded image. This image processing pipeline is built using Python Flask and SQLAlchemy, with images stored in an SQLite database. 

Unfortunately, since I could not run Salesforce BLIP Image Captioning Model (Large) on my computer, the Salesforce BLIP Image Captioning Model (Base) is used for this API pipeline instead. 

## Installation steps


## API documentation
1. Upload an Image

- Endpoint: POST /api/images
- Request: Multipart form-data with an image file (file parameter - only supports JPG and PNG images)
- Response: JSON object containing image ID and processing status

2. List all processing and processed images
- Endpoint: GET /api/images
- Response: JSON object listing all images' details including filename, image ID and processing status

3. Retrieve Metadata

- Endpoint: GET /api/images/<image_id>
- Response: JSON object containing filename, image ID, caption, processing time, processing status, thumbnail links and other metadata

4. Generate and Retrieve Thumbnails

- Endpoint: GET /api/images/<image_id>/thumbnails/<size>
- Response: JSON object with links to generated thumbnails (small / medium)

5. Get Processing Statistics

- Endpoint: GET /api/stats
- Response: JSON object containing number of images in the database, success and failure rates, and average processing 

## Processing pipeline explanation
1. Image Upload: The image is uploaded and stored in the database.
2. Metadata Extraction: The image format, dimensions, and other details are extracted.
3. Thumbnail Generation: Small (64x64) and medium (128x128) thumbnails are generated and stored.
4. AI Captioning: The BLIP model generates a caption based on the image content.
5. API Access: Users can retrieve metadata, thumbnails, and captions via API endpoints.
