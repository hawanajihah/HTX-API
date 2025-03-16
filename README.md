# HTX-API

## Project Overview
This API is an image processing pipeline designed to automatically process uploaded images, generate thumbnails, extract metadata, and provide AI-generated captions using the Salesforce BLIP Image Captioning Model. It also tracks processing time and maintains a database record for each uploaded image. This image processing pipeline is built using Python Flask and SQLAlchemy, with images being stored in an SQLite database. 

Unfortunately, since I could not run Salesforce BLIP Image Captioning Model (Large) on my computer, the Salesforce BLIP Image Captioning Model (Base) is used for this API pipeline instead. 

## Installation steps
### Prerequisites
Ensure that you have Python 3.8+ installed, along with ```pip```

### Steps
1. Clone the repository
```
git clone https://github.com/hawanajihah/HTX-API.git
cd HTX-API
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Run the API
```
python main.py
```
The API will be accessible at ```http://127.0.0.1:8000``` 

## API documentation
1. Upload an Image

- Endpoint: POST /api/images
- Request: Multipart form-data with file field (only supports JPG and PNG images)
- Response: JSON object containing image ID and processing status

```
{
    "image_id": 1,
    "status": "processed"
}
```

- Error handling:
    - No file uploaded: returns 400 and error message: "No file uploaded."

      ```
      {
         "error": "No file uploaded."
      }
      ```

    - Invalid image format (eg. GIF, PDF): returns 400 and error message: "Only JPEG and PNG files are allowed."

      ```
        {
          "error": "Invalid images. Only JPEG and PNG files are allowed."
        }
      ```

    - Processing failure: returns 500 with error message: "An unexpected error occurred while processing the image."

      ```
      {
          "error": "An unexpected error occurred while processing the image."
      }
      ```

      NOTE: by removing file.seek(0) and image = Image.open(file) from lines 92-93 in the main.py file, it would simulate a processing failure when uploading an image.
 
2. List all processing and processed images
- Endpoint: GET /api/images
- Response: JSON object listing all images' details including filename, image ID and processing status

```
[
    {
        "filename": "photo.png",
        "id": 1,
        "status": "processed"
    },
    {
        "filename": "screenshot.png",
        "id": 2,
        "status": "processed"
    },
    {
        "filename": "new_image.jpg",
        "id": 3,
        "status": "processed"
    }
]
```

3. Retrieve Image Details

- Endpoint: GET /api/images/<int:image_id>
- Response: JSON object containing filename, image ID, caption, processing time, processing status, thumbnail links and other metadata

```
{
    "data": {
        "caption": "the triangle logo",
        "filename": "screenshot.png",
        "id": 2,
        "metadata": {
            "format": "PNG",
            "height": 768,
            "size_bytes": 4196352,
            "width": 1366
        },
        "processed_at": "2025-03-14T10:51:16Z"
    },
    "error": null,
    "status": "processed",
    "thumbnails": {
        "medium": "http://localhost:8000/api/images/2/thumbnails/medium",
        "small": "http://localhost:8000/api/images/2/thumbnails/small"
    }
}
```

- Error handling
    - Invalid image ID: returns 404 and error message: "Image not found"

      ```
      {
          "error": "Image not found"
      }
      ```

    - UnidentifiedImageError: returns 400 and error message: "Processing failure"

      ```
      {
          "error": "Processing failure"
      }
      ```

4. Generate and Retrieve Thumbnails

- Endpoint: GET /api/images/<int:image_id>/thumbnails/<string:size>
- Response: Image of thumbnails (small / medium)
- Error handling
    - Invalid image ID: returns 404 and error message: "Image not found"

      ```
      {
          "error": "Image not found"
      }
      ```

    - UnidentifiedImageError: returns 400 and error message: "Processing failure"

      ```
      {
          "error": "Processing failure"
      }
      ```
      
    - Invalid size: returns 400 and error message: "Invalid thumbnail size. Choose 'small' or 'medium'."
      
      ```
      {
          "error": "Invalid thumbnail size. Choose 'small' or 'medium'."
      }
      ```
      

5. Get Processing Statistics

- Endpoint: GET /api/stats
- Response: JSON object containing number of images in the database, success and failure rates, and average processing 

```
{
    "average_processing_time": "0.86s (to 2 dp)",
    "images": {
        "failed_images": 2,
        "processed_images": 11,
        "total_images": 13
    },
    "success_failures_rate": {
        "failure_rate": "15.38%",
        "success_rate": "84.62%"
    }
}
```

## Processing pipeline explanation
1. Image Upload: The image is uploaded, validated and stored in the database. Only JPEG, JPG and PNG images are supported. The image is loaded into memory for processing.
2. Metadata Extraction: After the uploaded image is converted to PNG format for consistency, the image format, dimensions, and other details are extracted.
3. Thumbnail Generation: Small (150x150) and medium (300x300) thumbnails are generated and stored.
4. AI Captioning: The BLIP model generates a caption based on the image content.
5. API Access: Users can retrieve metadata, thumbnails, and captions via API endpoints. Processing statistics such as success and failure rates can be retrieved via the API endpoints.
6. The original image (converted to PNG) and its metadata are stored in an SQLite database. The processing status, processing time, and timestamp are recorded.

- The system uses SYNCHRONOUS processing instead of the Automated Image Processing. 
