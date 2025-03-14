# HTX-API

## Project Overview
This API is an image processing pipeline designed to automatically process uploaded images, generate thumbnails, extract metadata, and provide AI-generated captions using the Salesforce BLIP Image Captioning Model. The API is built using Python Flask and SQLAlchemy, with images stored in an SQLite database. 

## Installation steps


## API documentation
1. Upload an Image

Endpoint: POST /
Request: Multipart form-data with an image file (file parameter - only supports JPG and PNG images)
Response: Redirects to home page

2. Retrieve Metadata

Endpoint: GET /api/images/<image_id>
Response: JSON object containing image format, size, mode, and other metadata

3. Generate and Retrieve Thumbnails

Endpoint: GET /api/images/<image_id>/thumbnails/<size>
Response: JSON object with paths to generated thumbnails (small / medium)

4. Get Processing Statistics

Endpoint: GET /api/stats
Response: JSON object containing success and failure rates, and average processing times

## Example usage


## Processing pipeline explanation
1. Image Upload: The image is uploaded and stored in the database.
2. Metadata Extraction: The image format, dimensions, and other details are extracted.
3. Thumbnail Generation: Small (64x64) and medium (128x128) thumbnails are generated and stored.
4. AI Captioning: The BLIP model generates a caption based on the image content.
5. API Access: Users can retrieve metadata, thumbnails, and captions via API endpoints.
