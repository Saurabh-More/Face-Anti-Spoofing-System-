import cv2
import numpy as np
import tensorflow as tf
import sys
import os

# Usage: python process_video.py input_video.mp4 output_video.mp4
if len(sys.argv) != 3:
    print("Usage: python process_video.py input_video.mp4 output_video.mp4")
    sys.exit(1)

input_video_path = sys.argv[1]
output_video_path = sys.argv[2]

# Load trained model
model = tf.keras.models.load_model('face_antispoofing_model_new.h5')

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open video
cap = cv2.VideoCapture(input_video_path)

if not cap.isOpened():
    print(f"Error opening video file: {input_video_path}")
    sys.exit(1)

# Prepare VideoWriter for output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

# Initialize counters
real_count = 0
spoof_count = 0
total_faces_detected = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (224, 224))
        face_normalized = face_resized / 255.0
        face_reshaped = np.reshape(face_normalized, (1, 224, 224, 3))

        # Prediction
        prediction = model.predict(face_reshaped, verbose=0)[0][0]
        label = "Real" if prediction < 0.7 else "Spoof"

        # Count predictions
        total_faces_detected += 1
        if label == "Real":
            real_count += 1
        else:
            spoof_count += 1

        # Draw results
        color = (0, 255, 0) if label == "Real" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{label} ({prediction:.2f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    out.write(frame)

# Release resources
cap.release()
out.release()

# Final summary (prints to Node.js console!)
print("Total Faces Detected:", total_faces_detected)
print("Real Count:", real_count)
print("Spoof Count:", spoof_count)

if real_count > spoof_count:
    print("\nFINAL VERDICT: REAL FACE DETECTED")
elif spoof_count > real_count:
    print("\nFINAL VERDICT: SPOOF FACE DETECTED")
else:
    print("\nFINAL VERDICT: INCONCLUSIVE (Equal Real & Spoof Predictions)")
