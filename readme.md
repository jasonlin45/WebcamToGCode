# Webcam to GCode

This program converts webcam images to high contrast black and white images and its corresponding gcode.  Functionality for converting uploaded images exists as well.  

## Prerequisites/Dependencies

[Python 3](https://www.python.org/downloads/) must first be installed. \
Using [pip](https://pip.pypa.io/en/stable/), install dependencies.

```bash
pip install numpy
pip install opencv-python
pip install tkinter
pip install Pillow
```

## Usage

Running the main webcam interface
```bash
python main.py
```
Converting an image to gcode.  Arguments in brackets are optional. \
Note that output_file_name is the name of the file, the program automatically uses .png for images and .nc for gcode.

```bash
python gcode_gen.py input_file_path output_file_name [threshold] [horizontal_size_mm] [pixel_size_mm]
```
