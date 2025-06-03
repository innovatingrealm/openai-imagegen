# OpenAI Image Generation API - Setup Guide

This is a comprehensive FastAPI-based service for OpenAI image generation, editing, and variations that runs in Docker containers and can be easily integrated with n8n or used via curl commands.

## 🚀 Features

- **Text-to-Image Generation**: Generate images from text prompts
- **Image Editing**: Edit existing images with prompts and optional masks
- **Image Variations**: Create variations of existing images
- **Multiple Reference Images**: Generate images using multiple reference images
- **Multiple Models**: Support for DALL-E 2, DALL-E 3, and GPT-Image-1
- **Multiple Input Formats**: URLs, file uploads, base64 images
- **Configurable Output**: Size, quality, format options
- **Rate Limiting**: Built-in rate limiting
- **Health Checks**: API health monitoring
- **Automatic Saving**: Save generated images to disk
- **Comprehensive Logging**: Request/response logging

## 📁 Project Structure

```
openai-image-api/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── models.py              # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── generation.py      # Image generation endpoints
│   │   ├── edit.py           # Image editing endpoints
│   │   ├── variations.py     # Image variations endpoints
│   │   └── health.py         # Health check endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── openai_service.py  # OpenAI API service
│   └── middleware/
│       ├── __init__.py
│       ├── rate_limiter.py    # Rate limiting middleware
│       └── logging.py         # Logging middleware
├── generated-images/          # Generated images storage
├── logs/                     # Application logs
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .env.example            # Environment variables example
├── .gitignore             # Git ignore rules
└── SETUP_GUIDE.md         # This guide
```

## 🛠️ Installation & Setup

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Basic knowledge of REST APIs

### Step 1: Clone or Create Project

Create a new directory and add all the provided files:

```bash
mkdir openai-image-api
cd openai-image-api
```

### Step 2: Environment Configuration

1. Copy the environment example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=50000000
ALLOWED_IMAGE_FORMATS=png,jpg,jpeg,webp
DEFAULT_IMAGE_SIZE=1024x1024
DEFAULT_IMAGE_QUALITY=standard
RATE_LIMIT_PER_MINUTE=60
```

### Step 3: Create Required Directories

```bash
mkdir -p generated-images logs src/routers src/services src/middleware
```

### Step 4: Add Python Files

Create all the Python files as provided in the artifacts above. Make sure to create empty `__init__.py` files in each package directory:

```bash
# Create empty __init__.py files
touch src/__init__.py
touch src/routers/__init__.py
touch src/services/__init__.py
touch src/middleware/__init__.py
```

### Step 5: Build and Run with Docker Compose

```bash
# Build and start the service
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`

### Step 6: Verify Installation

Check if the service is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "openai_status": "healthy"
}
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 API Endpoints

### 1. Text-to-Image Generation

**Endpoint**: `POST /api/v1/images/generate`

```bash
curl -X POST "http://localhost:8000/api/v1/images/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1,
    "response_format": "png",
    "save_to_disk": true
  }'
```

### 2. Generate from Multiple Reference Images

**Endpoint**: `POST /api/v1/images/generate-from-references`

```bash
curl -X POST "http://localhost:8000/api/v1/images/generate-from-references" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a gift basket containing all these items",
    "image_urls": [
      "https://example.com/image1.png",
      "https://example.com/image2.png"
    ],
    "model": "gpt-image-1",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1,
    "save_to_disk": true
  }'
```

### 3. Image Editing

**Endpoint**: `POST /api/v1/images/edit`

```bash
curl -X POST "http://localhost:8000/api/v1/images/edit" \
  -F "image=@/path/to/your/image.png" \
  -F "prompt=Add a rainbow in the sky" \
  -F "model=dall-e-2" \
  -F "size=1024x1024" \
  -F "n=1" \
  -F "save_to_disk=true"
```

With mask for inpainting:
```bash
curl -X POST "http://localhost:8000/api/v1/images/edit" \
  -F "image=@/path/to/your/image.png" \
  -F "mask=@/path/to/your/mask.png" \
  -F "prompt=Replace the masked area with a lake" \
  -F "model=dall-e-2" \
  -F "size=1024x1024" \
  -F "n=1"
```

### 4. Image Variations

**Endpoint**: `POST /api/v1/images/variations`

```bash
curl -X POST "http://localhost:8000/api/v1/images/variations" \
  -F "image=@/path/to/your/image.png" \
  -F "model=dall-e-2" \
  -F "size=1024x1024" \
  -F "n=3" \
  -F "save_to_disk=true"
```

### 5. Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## 🔗 n8n Integration

### HTTP Request Node Configuration

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/v1/images/generate`
3. **Headers**: 
   - `Content-Type`: `application/json`
4. **Body**: JSON
```json
{
  "prompt": "{{ $json.prompt }}",
  "model": "dall-e-3",
  "size": "1024x1024",
  "quality": "standard",
  "n": 1,
  "save_to_disk": true
}
```

### Example n8n Workflow

```json
{
  "nodes": [
    {
      "parameters": {
        "url": "http://localhost:8000/api/v1/images/generate",
        "options": {
          "bodyContentType": "json"
        },
        "bodyParametersJson": {
          "prompt": "A cat wearing a wizard hat",
          "model": "dall-e-3",
          "size": "1024x1024",
          "quality": "standard",
          "n": 1,
          "save_to_disk": true
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [820, 300],
      "name": "Generate Image"
    }
  ]
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key (required) |
| `ENVIRONMENT` | `development` | Environment (development/production) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `50000000` | Max file size (50MB) |
| `ALLOWED_IMAGE_FORMATS` | `png,jpg,jpeg,webp` | Allowed image formats |
| `DEFAULT_IMAGE_SIZE` | `1024x1024` | Default image size |
| `DEFAULT_IMAGE_QUALITY` | `standard` | Default image quality |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit per minute |

### Model Options

- `dall-e-2`: Lower cost, supports variations and inpainting
- `dall-e-3`: Higher quality, larger resolutions
- `gpt-image-1`: Superior instruction following, multiple image inputs

### Size Options

- `1024x1024` (square)
- `1536x1024` (landscape)
- `1024x1536` (portrait)

### Quality Options

- `low`: Faster generation
- `standard`: Balanced quality/speed
- `hd`: Highest quality (DALL-E 3 only)

## 📊 Response Format

All endpoints return a consistent response format:

```json
{
  "success": true,
  "message": "Successfully generated 1 image(s)",
  "images": [
    {
      "index": 0,
      "b64_json": "base64_encoded_image_data",
      "filename": "generated_20240101_120000_0.png",
      "file_path": "generated-images/generated_20240101_120000_0.png",
      "revised_prompt": "A detailed prompt revision..."
    }
  ],
  "request_params": {
    "model": "dall-e-3",
    "prompt": "Original prompt",
    "size": "1024x1024",
    "quality": "standard",
    "n": 1
  }
}
```

## 🚨 Error Handling

Errors return HTTP status codes with descriptive messages:

```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message"
}
```

Common error codes:
- `400`: Bad request (invalid parameters)
- `429`: Rate limit exceeded
- `500`: Internal server error

## 📈 Monitoring & Logs

### Viewing Logs

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs openai-image-api

# View log files
tail -f logs/api.log
```

### Health Monitoring

The service includes health checks that monitor:
- API service availability
- OpenAI API connectivity
- Container health status

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**
   ```bash
   # Check if API key is set
   docker-compose exec openai-image-api env | grep OPENAI_API_KEY
   ```

2. **Port Already in Use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use different external port
   ```

3. **Permission Issues**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER generated-images logs
   ```

4. **Memory Issues**
   ```bash
   # Monitor container resources
   docker stats
   ```

### Debug Mode

Run in development mode for detailed debugging:

```bash
# Set environment to development
echo "ENVIRONMENT=development" >> .env

# Rebuild and run
docker-compose up --build
```

## 🔄 Updates & Maintenance

### Updating the Service

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose up --build -d
```

### Backing Up Generated Images

```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz generated-images logs

# Restore backup
tar -xzf backup-20240101.tar.gz
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify your OpenAI API key
3. Check the interactive documentation at `/docs`
4. Ensure proper file permissions

---

**Happy Image Generating! 🎨**