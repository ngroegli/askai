# Pattern: Advanced Image Extraction

**Tags:** `content`, `analysis`, `transformation`

## Purpose

The `advanced_image_extraction` pattern extracts a structured JSON representation of an image's content and metadata. It is designed to produce a machine-readable, reproducible "context profile" describing objects, text, faces, colors, scene labels, layout (bounding boxes), and technical metadata. This output is intended for downstream automation, indexing, search, or programmatic decision-making.

You are an image understanding system. Given an input image (file or URL), produce a single JSON object that describes the image contents and technical metadata. Your response MUST be valid JSON only — do not include any explanatory text, markdown, or code fences.

Follow the exact schema specified in the PATTERN CONFIGURATION section. Provide confidence scores (0.0-1.0) for detection outputs where applicable. When an item cannot be determined, use null for scalar values and empty arrays for lists. Do not introduce any additional top-level keys.

Focus on accuracy, concision, and returning values that are actionable for downstream systems.

## Functionality

* Accept an image via local file path or web URL as input
* Detect and list objects and their bounding boxes (normalized coordinates)
* Extract visible text (OCR) with language and confidence
* Detect faces and estimate attributes (age range, gender, expressions) with confidence
* Summarize dominant colors and palette
* Provide scene-level labels (e.g., "office", "beach") and composition hints
* Emit technical metadata (image dimensions, format, EXIF where available)
* Return a single JSON document that strictly follows the defined schema
* Analyze the image for the following categories: objects, text, faces, colors, scene, composition, and technical metadata.
* For each detected object include: name, normalized bounding_box {x,y,w,h} (0-1 relative to width/height), confidence (0-1), and optional attributes (e.g., color, brand, reading for text inside object).
* For OCR/text: extract contiguous text blocks, indicate language (ISO code if possible), bounding boxes and confidence per block.
* For faces: include bounding_box, confidence, and estimated attributes (age_range, gender, emotions with confidences).
* For colors: return an ordered palette (hex codes) and dominance scores.
* For scene: return up to 5 scene/label suggestions with confidences and an optional brief summary string.
* For all detections include confidence scores; if a model cannot provide a numeric confidence, approximate it based on internal heuristics.
* Ensure all numeric confidences are between 0.0 and 1.0 and bounding boxes are normalized between 0.0 and 1.0.
* Include an `image_metadata` object with the following keys: `filename` (string|null), `resolution` ({width:int,height:int}|null), `file_format` (string|null), `color_profile` (string|null), `dominant_colors` (array of hex strings), `size_bytes` (number|null), and `exif` (object|null).

## Pattern Inputs

```yaml
inputs:
  - name: image_url
    description: URL to an image on the web (e.g., a public JPG/PNG)
    type: text
    required: false
    group: image_source
    example: "https://example.com/sample.jpg"

  - name: image_file
    description: Local path to the image file
    type: image_file
    required: false
    group: image_source
    example: "/tmp/photo.png"

  - name: detail_level
    description: Level of detail in the JSON output
    type: select
    required: false
    ignore_undefined: true
    options:
      - brief
      - standard
      - full
    default: standard

  - name: max_objects
    description: Maximum number of detected objects to include (0 = unlimited)
    type: number
    required: false
    ignore_undefined: true
    default: 0
    min: 0
    max: 200

input_groups:
  - name: image_source
    description: Provide either a URL or a local file path to the image
    required_inputs: 1
```

## Pattern Outputs

```yaml
results:
  - name: image_profile
    description: JSON object describing the image according to the schema
    type: json
    required: true
    example: |
      {
        "description": "A busy city street at dusk with pedestrians and cars.",
        "objects": [
          {
            "name": "person",
            "bounding_box": {"x":0.12,"y":0.2,"w":0.18,"h":0.45},
            "confidence": 0.98,
            "attributes": {"clothing_color":"red"}
          }
        ],
        "text": [
          {"text":"SALE","language":"en","bounding_box":{"x":0.72,"y":0.10,"w":0.12,"h":0.06},"confidence":0.92}
        ],
        "faces": [
          {"bounding_box":{"x":0.13,"y":0.22,"w":0.06,"h":0.06},"confidence":0.95,"age_range":"25-34","gender":"female","emotions":{"smile":0.8}}
        ],
        "colors": {"palette":["#1f77b4","#ff7f0e"],"dominance":[0.6,0.4]},
        "scene": {"labels":[{"label":"urban street","confidence":0.91}],"summary":"City street scene at dusk"},
        "composition": {"orientation":"landscape","aspect_ratio":1.78},
        "image_metadata": {
          "filename": "Aurelia-aurita-3.jpg",
          "resolution": {"width": 1024, "height": 768},
          "file_format": "jpg",
          "color_profile": "sRGB",
          "dominant_colors": ["#0000FF", "#00BFFF", "#E0FFFF"],
          "size_bytes": 345678,
          "exif": null
        }
      }
```

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.0
  max_tokens: 2000
  custom_parameters: {}
```
