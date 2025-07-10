import os
import random
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class VideoToolApp:
    def __init__(self, master):
        self.master = master
        master.title("Tool video Ng Minh Nhat")
        master.geometry("420x500")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        self.reup_tab = tk.Frame(self.notebook)
        self.cut_tab = tk.Frame(self.notebook)

        self.notebook.add(self.reup_tab, text="Reup Video")
        self.notebook.add(self.cut_tab, text="Cắt Video")

        self.setup_reup_tab()
        self.setup_cut_tab()

    def setup_reup_tab(self):
        self.video_paths = []
        self.output_folder = ""
        self.flip_video = tk.BooleanVar()
        self.reverse_video = tk.BooleanVar()
        self.blur_video = tk.BooleanVar()
        self.color_mix = tk.BooleanVar()
        self.add_noise = tk.BooleanVar()
        self.use_random_watermark = tk.BooleanVar()
        self.watermark_folder = ""
        self.noise_strength = tk.DoubleVar(value=10.0)

        tk.Button(self.reup_tab, text="Chọn Video", command=self.choose_videos).pack(pady=5)
        tk.Button(self.reup_tab, text="Chọn thư mục xuất", command=self.choose_output_folder).pack(pady=5)

        form_frame = tk.Frame(self.reup_tab)
        form_frame.pack(pady=5)

        tk.Label(form_frame, text="Tỷ lệ khung hình:").grid(row=0, column=0, sticky="w")
        self.aspect_ratio = ttk.Combobox(form_frame, values=["Bản gốc", "9:16", "1:1", "16:9"], width=10)
        self.aspect_ratio.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Độ phân giải:").grid(row=1, column=0, sticky="w")
        self.resolution = ttk.Combobox(form_frame, values=["1080x1920", "720x1280"], width=10)
        self.resolution.grid(row=1, column=1, padx=5)

        tk.Label(form_frame, text="Tốc độ khung hình:").grid(row=2, column=0, sticky="w")
        self.framerate = ttk.Combobox(form_frame, values=["24", "25", "30"], width=10)
        self.framerate.grid(row=2, column=1, padx=5)

        tk.Label(form_frame, text="Tốc độ phát video:").grid(row=3, column=0, sticky="w")
        self.speed = ttk.Combobox(form_frame, values=["0.75", "1.0", "1.25"], width=10)
        self.speed.grid(row=3, column=1, padx=5)

        # Dòng các checkbox hiệu ứng
        effects_frame = tk.Frame(self.reup_tab)
        effects_frame.pack(pady=10)

        tk.Checkbutton(effects_frame, text="Lật", variable=self.flip_video).grid(row=0, column=0, padx=5, sticky="w")
        tk.Checkbutton(effects_frame, text="Ngược", variable=self.reverse_video).grid(row=0, column=1, padx=5, sticky="w")
        tk.Checkbutton(effects_frame, text="Nhòe", variable=self.blur_video).grid(row=0, column=2, padx=5, sticky="w")
        tk.Checkbutton(effects_frame, text="Màu", variable=self.color_mix).grid(row=0, column=3, padx=5, sticky="w")
        tk.Checkbutton(effects_frame, text="Nhiễu", variable=self.add_noise).grid(row=0, column=4, padx=5, sticky="w")

        # Noise
        noise_frame = tk.Frame(self.reup_tab)
        noise_frame.pack(pady=5)
        tk.Label(noise_frame, text="Mức nhiễu (1–100):").pack(side="left")
        tk.Entry(noise_frame, textvariable=self.noise_strength, width=5).pack(side="left", padx=5)

        # Watermark
        tk.Checkbutton(self.reup_tab, text="Watermark ngẫu nhiên", variable=self.use_random_watermark, command=self.toggle_watermark_mode).pack()
        self.select_watermark_btn = tk.Button(self.reup_tab, text="Chọn thư mục watermark", command=self.choose_watermark_folder)
        self.select_watermark_btn.pack(pady=5)

        tk.Button(self.reup_tab, text="Xử lý Video", command=self.process_videos, bg="#4CAF50", fg="white").pack(pady=15)

    def toggle_watermark_mode(self):
        if self.use_random_watermark.get():
            self.select_watermark_btn.config(state="normal")
        else:
            self.select_watermark_btn.config(state="normal")

    def choose_videos(self):
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.mov *.avi")])
        if files:
            self.video_paths = files
            messagebox.showinfo("Đã chọn", f"Đã chọn {len(files)} video.")

    def choose_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            messagebox.showinfo("Thư mục xuất", f"Đã chọn thư mục: {folder}")

    def choose_watermark_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.watermark_folder = folder
            messagebox.showinfo("Watermark folder", f"Đã chọn thư mục: {folder}")

    def get_aspect_filter(self, width, height):
        selected = self.aspect_ratio.get()
        if selected == "Bản gốc":
            return None
        elif selected == "9:16":
            return "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        elif selected == "1:1":
            return "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080"
        elif selected == "16:9":
            return "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"


    def get_watermark_filter(self, video_path):
        if not self.watermark_folder:
            return None
        files = [f for f in os.listdir(self.watermark_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not files:
            return None
        watermark_path = os.path.join(self.watermark_folder, random.choice(files))
        return f"movie='{watermark_path}'[wm];[in][wm]overlay=W-w-10:H-h-10"

    def process_videos(self):
        aspect = self.aspect_ratio.get()
        resolution = self.resolution.get()
        framerate = self.framerate.get()
        speed = self.speed.get()

        if not all([aspect, resolution, framerate, speed, self.output_folder]):
            messagebox.showerror("Thiếu thông tin", "Vui lòng chọn đầy đủ các tùy chọn và thư mục xuất.")
            return

        width, height = resolution.split("x")
        speed_filter = f"setpts={1/float(speed)}*PTS"
        atempo_filter = f"atempo={min(float(speed), 2)}"

        for path in self.video_paths:
            filename = os.path.basename(path)
            name, _ = os.path.splitext(filename)
            output_path = os.path.join(self.output_folder, name + f"_reup.mp4")

            filters = []

            if self.flip_video.get():
                filters.append("hflip")
            aspect_filter = self.get_aspect_filter(width, height)
            if aspect_filter:
                filters.append(aspect_filter)

            if self.reverse_video.get():
                filters.append("reverse")
            if self.blur_video.get():
                filters.append("boxblur=2:1")
            if self.color_mix.get():
                filters.append("eq=saturation=2.5:contrast=1.1")
            if self.add_noise.get():
                noise_strength = max(1, min(100, int(self.noise_strength.get())))
                filters.append(f"noise=alls={noise_strength}:allf=t+u")

            wm_filter = self.get_watermark_filter(path) if self.use_random_watermark.get() else None
            if wm_filter:
                filters.append(wm_filter)

            filters.append(speed_filter)
            vf_filter = ",".join(filters)

            cmd = [
                "ffmpeg", "-y", "-i", path,
                "-vf", vf_filter,
                "-filter:a", atempo_filter,
                "-r", framerate,
                output_path
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Lỗi", f"Xảy ra lỗi khi xử lý video: {path}\n{e}")

        messagebox.showinfo("Hoàn tất", "Đã xử lý xong tất cả video.")

    # --- Cut tab không thay đổi ---
    def setup_cut_tab(self):
        self.video_path = None
        self.output_folder_cut = None
        self.segment_entries = []

        top_frame = tk.Frame(self.cut_tab)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="Cắt theo đoạn", command=self.activate_segment_mode).grid(row=0, column=0, padx=10)
        tk.Button(top_frame, text="Cắt bằng giây", command=self.activate_equal_mode).grid(row=0, column=1, padx=10)

        tk.Button(self.cut_tab, text="Chọn video", command=self.choose_video_cut).pack(pady=5)
        tk.Button(self.cut_tab, text="Chọn thư mục xuất", command=self.choose_output_folder_cut).pack(pady=5)

        self.segment_mode_frame = tk.Frame(self.cut_tab)
        self.equal_mode_frame = tk.Frame(self.cut_tab)

        tk.Label(self.segment_mode_frame, text="Số đoạn muốn cắt:").pack()
        self.num_segments_entry = tk.Entry(self.segment_mode_frame)
        self.num_segments_entry.insert(0, "2")
        self.num_segments_entry.pack()

        tk.Button(self.segment_mode_frame, text="Tạo ô nhập thời gian", command=self.create_time_inputs).pack(pady=5)
        self.segment_frame = tk.Frame(self.segment_mode_frame)
        self.segment_frame.pack()

        tk.Label(self.equal_mode_frame, text="Độ dài mỗi đoạn (giây):").pack()
        self.equal_duration_entry = tk.Entry(self.equal_mode_frame)
        self.equal_duration_entry.insert(0, "10")
        self.equal_duration_entry.pack(pady=5)

        tk.Button(self.cut_tab, text="Cắt video", command=self.split_video).pack(pady=10)
        self.activate_segment_mode()

    def activate_segment_mode(self):
        self.equal_mode_frame.pack_forget()
        self.segment_mode_frame.pack()

    def activate_equal_mode(self):
        self.segment_mode_frame.pack_forget()
        self.equal_mode_frame.pack()

    def choose_video_cut(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if self.video_path:
            print(f"Video đã chọn: {self.video_path}")

    def choose_output_folder_cut(self):
        self.output_folder_cut = filedialog.askdirectory()
        if self.output_folder_cut:
            print(f"Thư mục xuất: {self.output_folder_cut}")

    def create_time_inputs(self):
        for widget in self.segment_frame.winfo_children():
            widget.destroy()
        self.segment_entries = []

        try:
            num_segments = int(self.num_segments_entry.get())
        except ValueError:
            print("Số đoạn không hợp lệ!")
            return

        for i in range(num_segments):
            row_frame = tk.Frame(self.segment_frame)
            row_frame.pack(pady=2)
            tk.Label(row_frame, text=f"Đoạn {i+1}: từ").pack(side="left")
            start_entry = tk.Entry(row_frame, width=7)
            start_entry.pack(side="left")
            tk.Label(row_frame, text="đến").pack(side="left")
            end_entry = tk.Entry(row_frame, width=7)
            end_entry.pack(side="left")
            self.segment_entries.append((start_entry, end_entry))

    def split_video(self):
        if not self.video_path or not self.output_folder_cut:
            print("Vui lòng chọn video và thư mục xuất!")
            return

        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", self.video_path
            ], capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
        except:
            print("Không thể đọc độ dài video.")
            return

        if self.segment_mode_frame.winfo_ismapped():
            self.split_custom(total_duration)
        elif self.equal_mode_frame.winfo_ismapped():
            try:
                equal_duration = float(self.equal_duration_entry.get())
                if equal_duration > 0:
                    self.split_evenly(total_duration, equal_duration)
                else:
                    print("Vui lòng nhập số giây > 0!")
            except:
                print("Số giây không hợp lệ!")

    def split_custom(self, total_duration):
        for idx, (start_entry, end_entry) in enumerate(self.segment_entries):
            try:
                start = float(start_entry.get())
                end_raw = end_entry.get().strip().lower()
                if end_raw == "end":
                    end = total_duration
                else:
                    end = float(end_raw)
                if not (0 <= start < end <= total_duration):
                    raise ValueError()
            except:
                print(f"Đoạn {idx+1} có thời gian không hợp lệ!")
                return

            output_file = os.path.join(self.output_folder_cut, f"part_{idx+1}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", self.video_path,
                "-ss", str(start), "-to", str(end),
                "-c", "copy", output_file
            ])

    def split_evenly(self, total_duration, segment_duration):
        idx = 1
        current = 0
        while current < total_duration:
            start = current
            end = min(current + segment_duration, total_duration)
            output_file = os.path.join(self.output_folder_cut, f"equal_part_{idx}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", self.video_path,
                "-ss", str(start), "-to", str(end),
                "-c", "copy", output_file
            ])
            current += segment_duration
            idx += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToolApp(root)
    root.mainloop()