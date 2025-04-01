# API Documentation

## Overview

DataStream Pro provides a RESTful API for data processing, analysis, and visualization. This document describes the available endpoints, request/response formats, and authentication requirements.

## Authentication

All API requests require authentication using either:

1. Bearer Token
2. API Key

### Bearer Token Authentication

Include the token in the Authorization header:

```http
Authorization: Bearer <your_token>
```

### API Key Authentication

Include the API key in the X-API-Key header:

```http
X-API-Key: <your_api_key>
```

## Rate Limiting

API requests are limited to 100 requests per minute per API key. The following headers are included in responses:

- `X-RateLimit-Limit`: Maximum number of requests per minute
- `X-RateLimit-Remaining`: Number of requests remaining in the current window
- `X-RateLimit-Reset`: Time when the rate limit window resets

## Endpoints

### Authentication

#### POST /api/v1/auth/token

Get access token.

**Request:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

### Datasets

#### GET /api/v1/datasets

List all datasets.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `sort`: Sort field (default: "created_at")
- `order`: Sort order (asc/desc)

**Response:**
```json
{
    "items": [
        {
            "id": "string",
            "name": "string",
            "source": "string",
            "description": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ],
    "total": 0,
    "page": 1,
    "limit": 10
}
```

#### POST /api/v1/datasets

Create a new dataset.

**Request:**
```json
{
    "name": "string",
    "source": "string",
    "description": "string"
}
```

**Response:**
```json
{
    "id": "string",
    "name": "string",
    "source": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### GET /api/v1/datasets/{dataset_id}

Get dataset details.

**Response:**
```json
{
    "id": "string",
    "name": "string",
    "source": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "data_points": [
        {
            "id": "string",
            "timestamp": "datetime",
            "value": "number",
            "metadata": {}
        }
    ]
}
```

### Analysis

#### POST /api/v1/datasets/{dataset_id}/analysis

Create a new analysis.

**Request:**
```json
{
    "type": "string",
    "parameters": {}
}
```

**Response:**
```json
{
    "id": "string",
    "type": "string",
    "parameters": {},
    "results": {},
    "created_at": "datetime",
    "creator_id": "string"
}
```

#### GET /api/v1/datasets/{dataset_id}/analysis

List analyses for a dataset.

**Response:**
```json
{
    "items": [
        {
            "id": "string",
            "type": "string",
            "parameters": {},
            "results": {},
            "created_at": "datetime",
            "creator_id": "string"
        }
    ],
    "total": 0
}
```

### Visualization

#### POST /api/v1/datasets/{dataset_id}/visualize

Create a visualization.

**Request:**
```json
{
    "type": "string",
    "parameters": {}
}
```

**Response:**
```json
{
    "id": "string",
    "type": "string",
    "parameters": {},
    "data": {},
    "created_at": "datetime"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "detail": "string"
}
```

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
    "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
    "detail": "Item not found"
}
```

### 429 Too Many Requests
```json
{
    "detail": "Too many requests"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## SDK Examples

### Python

```python
from datastream_pro import DataStreamPro

client = DataStreamPro(api_key="your_api_key")

# Create dataset
dataset = client.create_dataset(
    name="Climate Data",
    source="NOAA",
    description="Monthly temperature data"
)

# Add data points
client.add_data_points(
    dataset_id=dataset.id,
    data_points=[
        {"timestamp": "2024-01-01", "value": 25.5},
        {"timestamp": "2024-01-02", "value": 26.0}
    ]
)

# Create analysis
analysis = client.create_analysis(
    dataset_id=dataset.id,
    type="trend",
    parameters={"window": 7}
)

# Create visualization
visualization = client.create_visualization(
    dataset_id=dataset.id,
    type="line",
    parameters={"title": "Temperature Trend"}
)
```

### JavaScript

```javascript
const DataStreamPro = require('datastream-pro');

const client = new DataStreamPro({
    apiKey: 'your_api_key'
});

// Create dataset
const dataset = await client.createDataset({
    name: 'Climate Data',
    source: 'NOAA',
    description: 'Monthly temperature data'
});

// Add data points
await client.addDataPoints(dataset.id, [
    { timestamp: '2024-01-01', value: 25.5 },
    { timestamp: '2024-01-02', value: 26.0 }
]);

// Create analysis
const analysis = await client.createAnalysis(dataset.id, {
    type: 'trend',
    parameters: { window: 7 }
});

// Create visualization
const visualization = await client.createVisualization(dataset.id, {
    type: 'line',
    parameters: { title: 'Temperature Trend' }
});
``` 