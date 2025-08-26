import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk, ImageDraw, ImageFont
from rembg import remove
import io

class AdvancedStickerMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Telegram Sticker Maker")
        self.root.geometry("900x650")
        
        # Variables
        self.original_image = None
        self.sticker_image = None
        self.preview_image = None
        self.text = ""
        self.text_size = 40
        self.text_color = "#000000"
        self.font_path = "arial.ttf"  # مسیر فونت دلخواه روی سیستم خودتان
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab Editor
        self.tab_editor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_editor, text="Sticker Editor")
        
        self.canvas = tk.Canvas(self.tab_editor, width=512, height=512, bg='gray')
        self.canvas.pack(pady=10)
        
        # Controls Frame
        ctrl_frame = tk.Frame(self.tab_editor)
        ctrl_frame.pack(pady=5)
        
        tk.Button(ctrl_frame, text="Add Image", command=self.add_image).grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="Remove Background", command=self.remove_bg).grid(row=0, column=1, padx=5)
        tk.Button(ctrl_frame, text="Save Sticker", command=self.save_sticker).grid(row=0, column=2, padx=5)
        
        # Text Controls
        tk.Label(ctrl_frame, text="Text:").grid(row=1, column=0)
        self.text_entry = tk.Entry(ctrl_frame)
        self.text_entry.grid(row=1, column=1)
        self.text_entry.bind("<KeyRelease>", lambda e: self.update_text())
        
        tk.Label(ctrl_frame, text="Font Size:").grid(row=1, column=2)
        self.size_var = tk.IntVar(value=self.text_size)
        tk.Spinbox(ctrl_frame, from_=10, to=200, textvariable=self.size_var, width=5, command=self.update_text).grid(row=1, column=3)
        
        tk.Button(ctrl_frame, text="Text Color", command=self.choose_color).grid(row=1, column=4)
        
        # Tab Help
        self.tab_help = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_help, text="Help")
        help_text = """Telegram Sticker Maker Help:

1. Add your image using 'Add Image'.
2. Remove background with 'Remove Background'.
3. Add text with desired font size and color.
4. Preview updates live on canvas.
5. Save sticker (PNG 512x512, ≤512KB).
6. To create a sticker pack:
   - Open Telegram
   - Search for @Stickers bot
   - Use /newpack and follow instructions
   - Upload your PNG sticker
   - Repeat for all stickers in your pack
"""
        tk.Label(self.tab_help, text=help_text, justify='left').pack(padx=10, pady=10)
    
    # -------- Methods --------
    def add_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
        self.original_image = Image.open(file_path).convert("RGBA")
        self.original_image = self.original_image.resize((512,512), Image.Resampling.LANCZOS)
        self.sticker_image = self.original_image.copy()
        self.update_canvas()
    
    def remove_bg(self):
        if self.sticker_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        output = remove(self.sticker_image)
        self.sticker_image = Image.open(io.BytesIO(output)).convert("RGBA")
        self.update_canvas()
    
    def update_text(self):
        if self.sticker_image is None:
            return
        self.text = self.text_entry.get()
        self.text_size = self.size_var.get()
        self.update_canvas()
    
    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.text_color = color
            self.update_canvas()
    
    def update_canvas(self):
        if self.sticker_image is None:
            return
        preview = self.sticker_image.copy()
        if self.text:
            draw = ImageDraw.Draw(preview)
            try:
                font = ImageFont.truetype(self.font_path, self.text_size)
            except:
                font = ImageFont.load_default()
            w, h = draw.textsize(self.text, font=font)
            draw.text(((512-w)/2, (512-h)/2), self.text, font=font, fill=self.text_color)
        self.preview_image = ImageTk.PhotoImage(preview)
        self.canvas.create_image(0,0, anchor='nw', image=self.preview_image)
    
    def save_sticker(self):
        if self.sticker_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        final_image = self.sticker_image.copy()
        if self.text:
            draw = ImageDraw.Draw(final_image)
            try:
                font = ImageFont.truetype(self.font_path, self.text_size)
            except:
                font = ImageFont.load_default()
            w, h = draw.textsize(self.text, font=font)
            draw.text(((512-w)/2, (512-h)/2), self.text, font=font, fill=self.text_color)
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files","*.png")])
        if save_path:
            self.reduce_size(final_image, save_path)
            messagebox.showinfo("Saved", "Sticker saved successfully!")
    
    def reduce_size(self, image, path, max_kb=512):
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        # اگر حجم بیشتر از 512 کیلوبایت شد، تعداد رنگ ها کاهش پیدا می کند
        if buffer.getbuffer().nbytes/1024 > max_kb:
            image = image.convert("P", palette=Image.ADAPTIVE)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
        with open(path, "wb") as f:
            f.write(buffer.getvalue())

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedStickerMaker(root)
    root.mainloop()
