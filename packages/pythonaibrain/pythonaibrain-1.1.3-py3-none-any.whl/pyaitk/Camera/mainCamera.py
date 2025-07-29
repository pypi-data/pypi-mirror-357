import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
from datetime import datetime
from pyzbar import pyzbar

class Camera:
    def __init__(self, window):
        self.data = set()
        self.window = window
        self.window.title("📷 Cool Camera App")
        self.window.configure(bg="#1e1e1e")
        self.window.resizable(False, False)

        self.recording = False
        self.out = None

        # Video capture object
        self.video_capture = cv2.VideoCapture(0)

        # GUI Components
        self.label = Label(window, bg="#1e1e1e")
        self.label.pack(padx=10, pady=10)

        self.capture_button = Button(
            window, text="📸 Capture Image", command=self.capture_image,
            font=("Segoe UI", 12, "bold"), fg="white", bg="#4CAF50",
            activebackground="#45a049", relief="flat", width=20
        )
        self.capture_button.pack(pady=5)

        self.record_button = Button(
            window, text="🎥 Start Recording", command=self.toggle_recording,
            font=("Segoe UI", 12, "bold"), fg="white", bg="#2196F3",
            activebackground="#1976D2", relief="flat", width=20
        )
        self.record_button.pack(pady=5)

        self.quit_button = Button(
            window, text="❌ Quit", command=self.quit_app,
            font=("Segoe UI", 12, "bold"), fg="white", bg="#f44336",
            activebackground="#e53935", relief="flat", width=20
        )
        self.quit_button.pack(pady=10)

        self.update_frame()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        try:
            qr_codes=pyzbar.decode(frame)
            for qr_code in qr_codes:
                self.data.add(qr_code.data.decode('utf-8'))
        except:
            pass
        if ret:
            # Save frame if recording
            if self.recording and self.out:
                self.out.write(frame)

            # Convert BGR to RGB for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        self.window.after(10, self.update_frame)

    def capture_image(self):
        ret, frame = self.video_capture.read()
        if ret:
            filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, frame)
            print(f"✅ Image saved as {filename}")

    def toggle_recording(self):
        if not self.recording:
            filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 20.0
            frame_size = (
                int(self.video_capture.get(3)),
                int(self.video_capture.get(4))
            )
            self.out = cv2.VideoWriter(filename, fourcc, fps, frame_size)
            self.recording = True
            self.record_button.config(text="⏹️ Stop Recording", bg="#FF5722")
            print(f"🎥 Recording started: {filename}")
        else:
            self.recording = False
            self.out.release()
            self.out = None
            self.record_button.config(text="🎥 Start Recording", bg="#2196F3")
            print("🛑 Recording stopped.")

    def quit_app(self):
        if self.recording and self.out:
            self.out.release()
        self.video_capture.release()
        self.window.destroy()

    def return_data(self) -> set:
        return self.data

def Start() -> set:
    # Start the GUI app
    root = tk.Tk()
    app = Camera(root)
    root.mainloop()
    return app.return_data()
