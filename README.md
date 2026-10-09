# sRGB Image Processor

A small web app that finds the average red, green, and blue intensity of an uploaded image after sRGB gamma encoding is removed.

Built with Python (Flask, NumPy, Pillow), HTML, and CSS.

**Live site:** __https://srgb-image-processor.onrender.com/__

## What it does:
1. You upload an image (JPG, PNG, BMP, GIF, WebP, or TIFF, up to 10 MB).
2. The app converts the pixels to numbers between 0.0 and 1.0.
3. It removes the sRGB gamma curve, so values are linear.
4. It forms a preview of your image and the mean of each color channel.

Since grayscale images have no separate color channels, all three means are reported as 0.
Uploaded images are processed in memory and are not saved.

## The math:
Image files store brightness on a curved scale (gamma encoding). Each normalized value `C'` is converted back to a linear value `C`:

```
C = C' / 12.92                        if C' <= 0.04045
C = ((C' + 0.055) / 1.055) ^ 2.4      if C' > 0.04045
```

Because the scale is linear, the means look darker than the stored sRGB values.

## Run it locally
Python 3.9 or newer is required.

```bash
# 1. Download the project and move into the folder
git clone https://github.com/changathena/srgb-image-processor
cd srgb-image-processor

# 2. Install the packages
pip install -r requirements.txt

# 3. Start the app
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Project structure
```
srgb-image-processor/
├── app.py              # Flask server and image math
├── requirements.txt    # Python packages
├── templates/
│   └── index.html      # Page layout (Flask fills in the results)
└── static/
    └── style.css       # Styling
```

## Deployment
The app needs a host that runs Python. On [Render](https://render.com/), use:

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `gunicorn app:app`

Set `debug=False` in 'app.py` before deploying

## Author
Athena Chang, Purdue University
