import sys
from pyaitk import *
from pyaitk import Camera
from pyaitk import TTS
from flask import Flask, request, jsonify
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, Menu, simpledialog, Toplevel
from PIL import Image, ImageTk, ImageOps
import os
import webbrowser
from .PYAS import Server

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

server = Server()


class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Chat App with Image & Text Features")
        self.geometry("600x700")

        self.image_refs = []  # Prevent garbage collection
        self.loaded_images = []  # Store (PIL image, path)

        # Chat area
        self.chat_frame = ctk.CTkScrollableFrame(self, width=550, height=550)
        self.chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Input area
        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(padx=10, pady=(0, 10), fill="x")

        self.entry = ctk.CTkEntry(self.entry_frame, width=400, placeholder_text="Type your message here...")
        self.entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        self.image_button = ctk.CTkButton(self.entry_frame, text="📷 Image", command=self.upload_image)
        self.image_button.grid(row=0, column=2, padx=5)

        self.entry_frame.columnconfigure(0, weight=1)

    def send_message(self):
        message = self.entry.get().strip()
        if message:
            self.display_message("You", message)
            self.entry.delete(0, "end")
            self.generate_ai_reply(message)

    def display_message(self, sender, message):
        full_message = f"{sender}: {message}"
        label = ctk.CTkLabel(self.chat_frame, text=full_message, anchor="w", justify="left", wraplength=500)
        label.pack(anchor="w", padx=10, pady=4)
        label.bind("<Button-3>", lambda e: self.show_text_menu(e, label, full_message))

    def generate_ai_reply(self, message):
        response = ""
        brain = Brain()  # Assuming Brain is defined in pyaitk
        brain.load()
        msg_type = brain.predict_message_type(message)
        if msg_type == ['Question', 'Answer']:
            response = brain.process_messages(message)

        if response == 'CLICK_PHOTO':
            root = tk.Tk()
            Camera(root)
            root.mainloop()

        elif response == 'TTS':
            TTS(message).say()

        elif response[0] == "OPEN":
            webbrowser.open(response[1])
        else:

            label = ctk.CTkLabel(self.chat_frame, text=response, anchor="e", justify="left", wraplength=500)
            label.pack(anchor="e", padx=10, pady=4)
            label.bind("<Button-3>", lambda e: self.show_text_menu(e, label, response))

    def upload_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if filepath:
            img = Image.open(filepath)
            self.display_image(img, filepath)

    def display_image(self, image_obj, path=None):
        # Resize and convert to CTkImage
        img_resized = image_obj.resize((300, 300))
        ctk_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(300, 300))

        label = ctk.CTkLabel(self.chat_frame, image=ctk_img, text="")
        label.image = ctk_img
        label.pack(anchor="w", padx=10, pady=4)

        # Add right-click menu
        label.bind("<Button-1>", lambda e: self.show_image_menu(e, image_obj, path))

        self.image_refs.append(ctk_img)
        self.loaded_images.append((image_obj, path))

    def show_image_menu(self, event, image, path):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="💾 Save Image", command=lambda: self.ask_to_save_image(image))
        menu.add_command(label="✏️ Edit Image", command=lambda: self.edit_image(image))
        menu.add_command(label="🔁 Resend Image", command=lambda: self.display_image(image, path))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def show_text_menu(self, event, label, text):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="📝 Edit Text", command=lambda: self.edit_text(label, text))
        menu.add_command(label="💾 Save Text", command=lambda: self.save_text_to_file(text))
        menu.add_command(label="🔁 Resend Text", command=lambda: self.display_message("You", text.split(":", 1)[1].strip()))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def edit_text(self, label, old_text):
        new_text = simpledialog.askstring("Edit Message", "Edit your message:", initialvalue=old_text.split(":", 1)[1].strip())
        if new_text:
            new_label_text = f"{old_text.split(':', 1)[0]}: {new_text}"
            label.configure(text=new_label_text)

    def save_text_to_file(self, text):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Message"
        )
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    f.write(text)
                self.display_message("System", f"Text saved to: {save_path}")
            except Exception as e:
                self.display_message("System", f"Failed to save text: {e}")

    def ask_to_save_image(self, image_obj):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            title="Save Image As..."
        )
        if save_path:
            try:
                image_obj.save(save_path)
                self.display_message("System", f"Image saved to: {save_path}")
            except Exception as e:
                self.display_message("System", f"Failed to save image: {e}")

    def edit_image(self, img):
        editor = Toplevel(self)
        editor.title("Image Editor")
        editor.geometry("400x400")

        img_resized = img.resize((250, 250))
        img_tk = ImageTk.PhotoImage(img_resized)
        img_label = ctk.CTkLabel(editor, text="", image=img_tk)
        img_label.image = img_tk
        img_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(editor)
        btn_frame.pack(pady=10)

        def apply_grayscale():
            gray_img = ImageOps.grayscale(img)
            self.display_image(gray_img)

        def apply_rotate():
            rotated_img = img.rotate(90)
            self.display_image(rotated_img)

        ctk.CTkButton(btn_frame, text="Grayscale", command=apply_grayscale).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Rotate", command=apply_rotate).grid(row=0, column=1, padx=5)

        editor.mainloop()

class App:
    def __init__(self):
        option = sys.argv
        if len(option) > 1:
            if option[1] == '--gui' or option[1] == '-g':
                GUI()

            if option[1] == '--web' or option[1] == '-w':
                server.run()

            if option[1] == '--help' or option[1] == '-h':
                print('<======== Help ========>\nOpen With GUI : [--gui, -g]\nOpen With Website : [--web, -w]\nHelp : [--help, -h]\n\n')

        choice = input("<======= Choice =======>\n1. Open With GUI.\n2. Open With Website\n\n>>> ")

        if choice.isdigit():
            if choice == '1':
                GUI()

            elif choice == '2':
                server.run()

            else:
                print(f'Invalid option {choice}')

        else:
            if choice.lower() == 'open with gui':
                GUI()

            elif choice.lower() == 'open with website' or choice.lower() == 'open with web':
                server.run()

            else:
                print(f'Invalid option {choice}')


__all__ = [
    "App",
    "Server",
    "GUI",
    "server"
]

__version__ = '1.0.9'
