import shutil
import whisper
from pathlib import Path
import os

# Download and cache the model using openai-whisper
MODEL_NAME = "small"
print(f"Downloading Whisper {MODEL_NAME} model using openai-whisper...")
model = whisper.load_model(MODEL_NAME)

# Find the cache directory
cache_dir = Path.home() / ".cache" / "whisper"

# Find the downloaded model file (usually ggml-small.bin or similar)
model_files = list(cache_dir.rglob("*small*"))
if not model_files:
    print("Model file not found in cache. Exiting.")
    exit(1)

# Set the destination directory (same as this script's directory)
dest_dir = Path(__file__).resolve().parent / "whisper-model"
dest_dir.mkdir(parents=True, exist_ok=True)

# Copy all relevant files
for file in model_files:
    dest_file = dest_dir / file.name
    print(f"Copying {file} to {dest_file}")
    shutil.copy2(file, dest_file)

print(f"All model files copied to {dest_dir}")

# Optionally, remove from cache
delete = input("Do you want to remove the model from the cache directory? (y/n): ").strip().lower()
if delete == 'y':
    for file in model_files:
        print(f"Removing {file}")
        os.remove(file)
    print("Model files removed from cache.")
else:
    print("Model files left in cache.")
