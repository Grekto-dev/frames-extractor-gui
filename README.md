# Frame Extractor Pro

A powerful, user-friendly Python application designed to extract high-quality frames from video files. Featuring a modern GUI built with PyQt6, it offers advanced visualization tools, batch exporting, and a responsive interface.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🚀 Features

- **Drag & Drop Support**: Easily load videos by dragging them into the interface or using the file picker.
- **Automated Extraction**: Extract every frame of a video with a real-time progress bar.
- **Advanced Frame Viewer**:
    - **Zoom & Pan**: Use the mouse scroll wheel to zoom (up to 50% min limit) and drag the image to explore details.
    - **Fast Navigation**: Navigate through frames using `<` and `>` buttons. Hold the buttons to scroll quickly through the timeline.
- **Responsive Gallery**: A dynamic flow layout that adjusts the number of columns automatically as you resize the window.
- **Batch Exporting**: Save all frames or only selected ones in **JPG** or **PNG** formats.
- **Internationalization (i18n)**: Full support for **English (US)** and **Portuguese (Brazil)**.
- **State Persistence**: The app remembers your language preference for the next session.
- **Automatic Cleanup**: Temporary files are managed and deleted automatically upon closing the program to save disk space.

---

## 🛠️ Tech Stack

- **Python 3.x**
- **PyQt6**: For the modern Graphical User Interface.
- **OpenCV (cv2)**: For high-speed video processing and frame extraction.
- **Pillow**: For image handling and manipulation.
- **Logging**: Integrated terminal logging for real-time debugging.

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/frame-extractor-pro.git](https://github.com/your-username/frame-extractor-pro.git)
cd frame-extractor-pro

```

### 2. Install Dependencies

The program includes an automatic dependency checker, but you can install them manually via pip:

```bash
pip install PyQt6 opencv-python Pillow

```

---

## 🚦 How to Use

1. **Run the Application**:
* On Windows: Double-click `executar.bat`.
* Via Terminal: `python extrator_frames.py`.


2. **Select Language**: Choose between Portuguese or English in the top-left corner.
3. **Load a Video**: Drag a video file (`.mp4`, `.avi`, `.mkv`, `.mov`) into the app or click **Open Video**.
4. **Browse Frames**: Click on any thumbnail to view it in high resolution on the right panel.
5. **Zoom & Move**: Use the scroll wheel to zoom into a frame and click-and-drag to move the view.
6. **Export**:
* Check the boxes of the frames you want.
* Choose the output format (JPG/PNG).
* Click **Save Selected** or **Save All**.



---

## 📂 Project Structure

* `extrator_frames.py`: The main Python script containing the GUI logic and processing threads.
* `executar.bat`: A convenient batch script for Windows users to launch the app.
* `tempfile/`: (Dynamic) The app uses the system's temporary directory to store cache, ensuring a clean workspace.

---

## 📝 Logging & Debugging

The application provides a detailed log in the terminal. It tracks:

* Dependency verification.
* System OS detection.
* Temporary folder creation/cleanup.
* Video metadata (Total frames, path).
* Exporting status.

---

## 👨‍💻 Author

**Pedro Nogueira**

* Version: 1.0.0

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

```
