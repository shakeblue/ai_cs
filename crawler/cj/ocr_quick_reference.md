# OCR Quick Reference Guide

## TL;DR - Best Choice for Korean E-commerce

**Recommended: PaddleOCR**

```bash
pip install paddleocr paddlepaddle-gpu
```

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='korean')
results = ocr.ocr('image.jpg')
```

**Why?** Free, fast (25 img/sec), excellent Korean accuracy (3.1% CER), small model (<10MB)

---

## Quick Comparison Table

| Solution | Cost | Accuracy (KO) | Speed | Setup | When to Use |
|----------|------|---------------|-------|-------|-------------|
| **PaddleOCR** | Free | ★★★★★ | Very Fast | Easy | **Default choice - best overall** |
| **EasyOCR** | Free | ★★★★★ | Moderate | Very Easy | Simple API, low-quality images |
| **Naver Clova** | $6k/100k | ★★★★★ | Fast | Moderate | Maximum Korean accuracy, budget available |
| **Google Vision** | $150/100k | ★★★★☆ | Very Fast | Easy | Quick setup, cloud-based |
| **Gemini Flash** | $50/100k | ★★★☆☆ | Very Fast | Easy | Cheapest cloud, document understanding |
| **Tesseract** | Free | ★★★☆☆ | Fast | Moderate | CPU-only environment |

---

## Installation Cheat Sheet

### PaddleOCR (Recommended)
```bash
# GPU version
pip install paddleocr paddlepaddle-gpu

# CPU version
pip install paddleocr paddlepaddle
```

### EasyOCR
```bash
pip install easyocr
```

### Tesseract
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor
pip install pytesseract

# macOS
brew install tesseract tesseract-lang
pip install pytesseract
```

### Cloud APIs
```bash
# Google Vision
pip install google-cloud-vision

# AWS Textract
pip install boto3

# Azure OCR
pip install azure-cognitiveservices-vision-computervision

# Gemini
pip install google-generativeai
```

---

## Code Examples

### PaddleOCR - Basic Usage
```python
from paddleocr import PaddleOCR

# Initialize
ocr = PaddleOCR(use_angle_cls=True, lang='korean', use_gpu=True)

# Extract text
results = ocr.ocr('image.jpg', cls=True)

# Process results
for line in results[0]:
    bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    text = line[1][0]  # Extracted text
    confidence = line[1][1]  # Confidence score (0-1)
    print(f"{text} ({confidence:.2f})")
```

### EasyOCR - Basic Usage
```python
import easyocr

# Initialize
reader = easyocr.Reader(['ko', 'en'], gpu=True)

# Extract text
results = reader.readtext('image.jpg')

# Process results
for bbox, text, confidence in results:
    print(f"{text} ({confidence:.2f})")
```

### Tesseract - Basic Usage
```python
import pytesseract
from PIL import Image

# Extract text
text = pytesseract.image_to_string(
    Image.open('image.jpg'),
    lang='kor+eng'
)
print(text)

# With detailed data
data = pytesseract.image_to_data(
    Image.open('image.jpg'),
    lang='kor+eng',
    output_type=pytesseract.Output.DICT
)
```

### Google Vision API
```python
from google.cloud import vision

# Initialize
client = vision.ImageAnnotatorClient()

# Load image
with open('image.jpg', 'rb') as image_file:
    content = image_file.read()

# Detect text
image = vision.Image(content=content)
response = client.text_detection(image=image)

# Process results
texts = response.text_annotations
if texts:
    print(f"Full text: {texts[0].description}")
```

### Gemini 1.5 Flash (Cost-effective LLM)
```python
import google.generativeai as genai

# Configure
genai.configure(api_key='YOUR_API_KEY')

# Initialize model
model = genai.GenerativeModel('gemini-1.5-flash')

# Upload and process
sample_file = genai.upload_file(path='image.jpg')
response = model.generate_content([
    "Extract all text from this image in Korean and English",
    sample_file
])
print(response.text)
```

---

## Performance Quick Reference

### Speed (images per second, GPU)
- PaddleOCR: **25 img/sec**
- Tesseract: **30 img/sec** (CPU)
- EasyOCR: **12 img/sec**
- Cloud APIs: **18-20 img/sec** (network dependent)

### Accuracy (Character Error Rate for Korean)
- Naver Clova: **2.1%** (best)
- KLOCR: **2.3%**
- Google Vision: **2.5%**
- PaddleOCR: **3.1%**
- EasyOCR: **3.8%**
- Tesseract: **8.2%** (worst)

*Lower CER = better accuracy*

### Cost (100,000 images)
- Free (PaddleOCR, EasyOCR, Tesseract): **$0-20** (electricity)
- Gemini Flash: **$50**
- Google Vision / AWS / Azure: **$140-150**
- GPT-4 Vision: **$200**
- Naver Clova: **$6,000**

---

## Decision Tree

```
Need OCR for Korean text?
│
├─ Budget unlimited?
│  ├─ YES → Naver Clova OCR (best Korean accuracy)
│  └─ NO → Continue...
│
├─ Have GPU?
│  ├─ YES → PaddleOCR (recommended for 90% of cases)
│  └─ NO → Tesseract (CPU-only) or Google Vision API
│
├─ Need document understanding?
│  ├─ YES → Gemini 1.5 Flash ($50/100k) or Claude Vision
│  └─ NO → Stick with PaddleOCR
│
└─ Data privacy critical?
   ├─ YES → PaddleOCR (self-hosted)
   └─ NO → Google Vision API (easy cloud option)
```

---

## Hybrid Approach (Recommended for Production)

```python
class HybridOCR:
    def __init__(self):
        self.paddle = PaddleOCR(lang='korean', use_gpu=True)
        # self.clova_api = ClovaOCR()  # If budget allows

    def extract_text(self, image_path):
        # Try PaddleOCR first (fast, free)
        results = self.paddle.ocr(image_path)

        # Calculate average confidence
        avg_conf = self._calculate_confidence(results)

        # If low confidence, fallback to premium service
        if avg_conf < 0.70:
            # Uncomment if using Naver Clova fallback
            # return self.clova_api.recognize(image_path)
            pass

        return self._extract_text(results)

    def _calculate_confidence(self, results):
        if not results or not results[0]:
            return 0.0
        confidences = [line[1][1] for line in results[0]]
        return sum(confidences) / len(confidences)

    def _extract_text(self, results):
        if not results or not results[0]:
            return ""
        return "\n".join([line[1][0] for line in results[0]])
```

**Benefits:**
- 90% of requests handled by free PaddleOCR
- 10% fallback to premium service for difficult cases
- Optimal cost-accuracy balance

---

## Common Issues & Solutions

### Issue: Low accuracy on Korean text
**Solution:**
1. Use `lang='korean'` parameter
2. Try PaddleOCR or EasyOCR (better than Tesseract for Korean)
3. Pre-process image (denoise, increase contrast)

### Issue: Slow processing
**Solution:**
1. Enable GPU: `use_gpu=True`
2. Use PaddleOCR (fastest among deep learning models)
3. Consider cloud APIs for high throughput

### Issue: Mixed Korean-English not detected
**Solution:**
1. PaddleOCR: Automatically handles mixed text
2. EasyOCR: `Reader(['ko', 'en'])`
3. Tesseract: `lang='kor+eng'`

### Issue: Rotated or skewed text
**Solution:**
1. PaddleOCR: `use_angle_cls=True`
2. EasyOCR: Built-in rotation handling
3. Pre-process: Auto-rotate image before OCR

### Issue: Low quality / noisy images
**Solution:**
1. Use EasyOCR (best for low-quality images)
2. Pre-process: Denoise, sharpen, increase contrast
3. Try multiple OCR engines and combine results

---

## Image Pre-processing Tips

```python
import cv2
import numpy as np

def preprocess_image(image_path):
    """Improve OCR accuracy with preprocessing"""
    # Read image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray)

    # Increase contrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrasted = clahe.apply(denoised)

    # Threshold (binarization)
    _, binary = cv2.threshold(
        contrasted, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Save preprocessed image
    preprocessed_path = 'preprocessed_' + image_path
    cv2.imwrite(preprocessed_path, binary)

    return preprocessed_path

# Usage
preprocessed = preprocess_image('noisy_image.jpg')
results = ocr.ocr(preprocessed)
```

---

## Resource Requirements

| Solution | RAM | GPU VRAM | CPU | Disk Space |
|----------|-----|----------|-----|------------|
| PaddleOCR | 2-4GB | 2GB+ (optional) | 2+ cores | 500MB |
| EasyOCR | 4-8GB | 8GB+ (required) | 4+ cores | 2GB |
| Tesseract | 1-2GB | N/A | 1+ core | 100MB |
| Surya | 4-8GB | 8-12GB | 4+ cores | 1GB |
| TrOCR | 4-8GB | 8-12GB | 4+ cores | 2GB |
| Cloud APIs | <1GB | N/A | 1+ core | <100MB |

---

## Language Support Quick Check

| Solution | Korean | Japanese | Chinese | English | Others |
|----------|--------|----------|---------|---------|--------|
| PaddleOCR | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent | 80+ |
| EasyOCR | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent | 80+ |
| Tesseract | ⚠️ Good | ⚠️ Good | ⚠️ Good | ✅ Excellent | 116 |
| Naver Clova | ✅ Best | ✅ Excellent | ⚠️ Limited | ✅ Excellent | 3 |
| Google Vision | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent | 50+ |
| Gemini | ⚠️ Good | ⚠️ Good | ⚠️ Good | ✅ Excellent | 10+ |

---

## Next Steps

1. **Install PaddleOCR**
   ```bash
   pip install paddleocr paddlepaddle-gpu
   ```

2. **Test with sample image**
   ```python
   from paddleocr import PaddleOCR
   ocr = PaddleOCR(lang='korean')
   result = ocr.ocr('test_image.jpg')
   print(result)
   ```

3. **Integrate with crawler**
   - See `/home/long/ai_cs/crawler/cj/OCR_COMPARISON_GUIDE.md` Section 7.2

4. **Optimize for production**
   - Implement hybrid approach
   - Add error handling
   - Monitor accuracy metrics
   - Consider fallback to Naver Clova for difficult cases

---

## Additional Resources

- **Full comparison guide:** `/home/long/ai_cs/crawler/cj/OCR_COMPARISON_GUIDE.md`
- **PaddleOCR docs:** https://github.com/PaddlePaddle/PaddleOCR
- **EasyOCR docs:** https://github.com/JaidedAI/EasyOCR
- **Tesseract docs:** https://github.com/tesseract-ocr/tesseract
- **Google Vision:** https://cloud.google.com/vision/docs/ocr
- **Naver Clova:** https://www.ncloud.com/product/aiService/ocr
