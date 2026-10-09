import base64 # turns image bytes into plain text so a web page can show them
import io # lets us treat data in memory like a file (no saving to disk)

import numpy as np # fast math on big grids of numbers (our image pixels)
from flask import Flask, render_template, request # web framework
from PIL import Image, UnidentifiedImageError # Pillow: opens and edits images

# app setup

# creates web app
app = Flask(__name__)

# rejects uploaders >10MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# file endings that are acceptable
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "webp", "tif", "tiff"}

# pillow describes image img with a "mode" (how pixels are stored)
GRAYSCALE_MODES = {"1", "L", "LA", "I", "I;16"}

# math functions

def normalize_image(img_array):
    # NumPy divides every number in array at once
    return img_array / 255.0

def linearize_image(img_array):
    return np.where(
        img_array <= 0.04045,
        img_array / 12.92,
        ((img_array + 0.055) / 1.055) ** 2.4,
    )

def mean_channel(img_array, channel):
    if img_array.ndim == 2:
        return 0.0
    return float(np.mean(img_array[:, :, channel]))

def load_image(file_storage):
    image = Image.open(file_storage.stream)
    image.load()

    if image.mode in GRAYSCALE_MODES:
        return image.convert("L"), True
    return image.convert("RGB"), False

def make_preview(image, max_size=720):
    preview = image.copy()
    preview.thumbnail((max_size, max_size))
    buffer = io.BytesIO()
    preview.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")

def analyze(file_storage):
    image, is_grayscale = load_image(file_storage)
    img_array = np.array(image)
    normalized = normalize_image(img_array)
    lienarized = linearize_image(normalized)
    means = {
        "Red": mean_channel(linearized, 0),
        "Green": mean_channel(linearized, 1),
        "Blue": mean_channel(linearized, 2),
    }

    return {
        "filename": file_storage.filename,
        "means": means,
        "grayscale": is_grayscale,
        "preview": make_preview(image),
        "size": f"{image.width} x {image.height} px",
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        file = request.files.get("image")
        extension = (
            file.filename.rsplit(".", 1)[-1].lower()
            if file and "." in file.filename
            else ""
        )

        if not file or file.filename == "":
            error = "Choose an image file to analyze."
        elif extension not in ALLOWED_EXTENSIONS:
            error = "That file type isn't supported. Upload a JPG, PNG, BMP, GIF, WebP, or TIFF image."
        else:
            try:
                result = analyze(file)
            except (UnidentifiedImageError, OSError):
                error = "That file couldn't be read as an image. Try a different file."

    return render_template("index.html", result=result, error=error)

@app.errorhandler(413)
def file_too_large(_):
    return render_template(
        "index.html", result=None, error="That image is over 10 MB. Upload a smaller file."
    ), 413

if __name__ == "__main__":
    app.run(debug=True)