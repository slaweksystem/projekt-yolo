import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import glob
import os
from ultralytics import YOLO

# Load YOLO model
model = YOLO('best.pt')

# Global state
image_paths = []
current_index = 0

# GUI setup
root = tk.Tk()
root.title("YOLO Object Detection Viewer")

# --- Top button frame ---
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, pady=10)

# --- Main display frame ---
display_frame = tk.Frame(root)
display_frame.pack(side=tk.TOP)

# Labels for images
original_label = tk.Label(display_frame)
original_label.pack(side=tk.LEFT, padx=10)

annotated_label = tk.Label(display_frame)
annotated_label.pack(side=tk.LEFT, padx=10)

# --- Frame for detected labels ---
label_frame = tk.Frame(display_frame)
label_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

label_title = tk.Label(label_frame, text="Detected Objects", font=("Arial", 12, "bold"))
label_title.pack()

label_list = tk.Text(label_frame, width=25, height=30)
label_list.pack()

def load_folder():
    global image_paths, current_index
    folder = filedialog.askdirectory()
    if not folder:
        return

    image_paths = sorted(glob.glob(os.path.join(folder, '*.[jp][pn]*g')))
    if image_paths:
        current_index = 0
        show_image()

def show_image():
    global current_index
    if not image_paths:
        return

    # Load image
    img_path = image_paths[current_index]
    img = cv2.imread(img_path)

    # Run YOLO inference
    results = model(img)[0]
    annotated = results.plot()

    # Convert OpenCV BGR to RGB and create PIL images
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ann_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    img_pil = Image.fromarray(img_rgb)
    ann_pil = Image.fromarray(ann_rgb)

    # Resize images
    max_size = (400, 400)
    #img_pil.thumbnail(max_size, Image.ANTIALIAS)
    #ann_pil.thumbnail(max_size, Image.ANTIALIAS)

    # Convert to Tkinter images
    img_tk = ImageTk.PhotoImage(img_pil)
    ann_tk = ImageTk.PhotoImage(ann_pil)

    original_label.configure(image=img_tk)
    original_label.image = img_tk

    annotated_label.configure(image=ann_tk)
    annotated_label.image = ann_tk

    # Update label list
    label_list.delete(1.0, tk.END)
    object_names = [model.names[int(box.cls)] for box in results.boxes]
    if object_names:
        for name in object_names:
            label_list.insert(tk.END, f"{name}\n")
    else:
        label_list.insert(tk.END, "No objects detected")

    root.title(f"Viewing: {os.path.basename(img_path)}")

def next_image():
    global current_index
    if image_paths and current_index < len(image_paths) - 1:
        current_index += 1
        show_image()

def prev_image():
    global current_index
    if image_paths and current_index > 0:
        current_index -= 1
        show_image()

# Buttons
btn_load = tk.Button(button_frame, text="Load Folder", command=load_folder)
btn_prev = tk.Button(button_frame, text="Previous", command=prev_image)
btn_next = tk.Button(button_frame, text="Next", command=next_image)

btn_load.pack(side=tk.LEFT, padx=5)
btn_prev.pack(side=tk.LEFT, padx=5)
btn_next.pack(side=tk.LEFT, padx=5)

# Start GUI loop
root.mainloop()
