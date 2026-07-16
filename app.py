import asyncio
import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pygame
from tts_engine import TTSEngine

pygame.mixer.init()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TTSApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Dịch thuật & Chuyển Văn Bản Thành Giọng Nói (TTS)")
        self.geometry("980x750")

        self.raw_voices = []
        self.voices_dict = {}
        self.supported_langs = {}
        self.is_playing_preview = False
        self.preview_file_path = None
        
        self.setup_ui()
        self.load_languages_and_voices()

    def setup_ui(self):
        self.lbl_title = ctk.CTkLabel(
            self,
            text="TRANSLATION & TEXT TO SPEECH PRO",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lbl_title.pack(pady=15)

        # Thanh cấu hình dịch thuật
        self.frame_trans_ctrl = ctk.CTkFrame(self)
        self.frame_trans_ctrl.pack(fill="x", padx=20, pady=5)

        self.lbl_trans = ctk.CTkLabel(self.frame_trans_ctrl, text="Ngôn ngữ đích (Dịch sang):", text_color="gray")
        self.lbl_trans.pack(side="left", padx=10, pady=10)

        self.combo_lang = ctk.CTkComboBox(
            self.frame_trans_ctrl, 
            values=["Đang tải ngôn ngữ..."], 
            width=220,
            command=self.on_language_change
        )
        self.combo_lang.pack(side="left", padx=10, pady=10)

        self.btn_translate = ctk.CTkButton(
            self.frame_trans_ctrl,
            text="🔄 Dịch văn bản",
            width=150,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.start_translation,
        )
        self.btn_translate.pack(side="left", padx=10, pady=10)

        # KHU VỰC CHIA ĐÔI
        self.frame_split_input = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_split_input.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.frame_split_input.grid_columnconfigure(0, weight=1, uniform="group1")
        self.frame_split_input.grid_columnconfigure(1, weight=1, uniform="group1")
        self.frame_split_input.grid_rowconfigure(0, weight=1)

        # Văn bản gốc
        self.frame_left = ctk.CTkFrame(self.frame_split_input)
        self.frame_left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.lbl_left_title = ctk.CTkLabel(self.frame_left, text="VĂN BẢN GỐC (BẤT KỲ NGÔN NGỮ NÀO)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3498db")
        self.lbl_left_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.txt_input = ctk.CTkTextbox(self.frame_left, font=ctk.CTkFont(size=14), height=280)
        self.txt_input.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.txt_input.insert("0.0", "Nhập hoặc dán văn bản gốc vào đây để dịch...")

        # Văn bản dịch
        self.frame_right = ctk.CTkFrame(self.frame_split_input)
        self.frame_right.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.lbl_right_title = ctk.CTkLabel(self.frame_right, text="BẢN DỊCH (GIỌNG ĐỌC SẼ PHÁT TỪ ĐÂY)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71")
        self.lbl_right_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.txt_translated = ctk.CTkTextbox(self.frame_right, font=ctk.CTkFont(size=14), height=280)
        self.txt_translated.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.txt_translated.insert("0.0", "Kết quả dịch sẽ xuất hiện tại đây...")

        # KHU VỰC CẤU HÌNH GIỌNG ĐỌC
        self.frame_voice = ctk.CTkFrame(self)
        self.frame_voice.pack(fill="x", padx=20, pady=5)

        self.lbl_voice = ctk.CTkLabel(self.frame_voice, text="Chọn giọng đọc chuẩn ngữ cảnh:", text_color="gray")
        self.lbl_voice.pack(side="left", padx=10, pady=10)

        self.combo_voice = ctk.CTkComboBox(self.frame_voice, width=500)
        self.combo_voice.pack(side="left", padx=10, pady=10)

        self.btn_preview = ctk.CTkButton(
            self.frame_voice,
            text="🔊 Nghe thử bản dịch",
            width=160,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.start_preview,
        )
        self.btn_preview.pack(side="left", padx=10, pady=10)

        # Tiến độ
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Đang khởi tạo hệ thống...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="gray",
        )
        self.lbl_status.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=940)
        self.progress_bar.pack(padx=20, pady=5)
        self.progress_bar.set(0)

        self.btn_convert = ctk.CTkButton(
            self,
            text="Xuất bản dịch ra file MP3",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.start_conversion,
        )
        self.btn_convert.pack(pady=15)

    def load_languages_and_voices(self):
        def target():
            try:
                # 1. Tải danh sách ngôn ngữ dịch thuật
                self.supported_langs = TTSEngine.get_supported_languages()
                lang_names = sorted(list(self.supported_langs.keys()))
                self.combo_lang.configure(values=lang_names)
                
                default_lang = "Tiếng Việt"
                if "Tiếng Việt" in lang_names:
                    self.combo_lang.set("Tiếng Việt")
                elif lang_names:
                    self.combo_lang.set(lang_names[0])
                    default_lang = lang_names[0]

                # 2. Tải toàn bộ danh sách giọng nói Microsoft Edge TTS
                self.raw_voices = asyncio.run(TTSEngine.get_all_voices())
                
                # Cập nhật danh sách giọng nói ban đầu
                self.filter_voices_by_lang(default_lang)
                self.lbl_status.configure(text="Hệ thống đã sẵn sàng!", text_color="gray")
            except Exception as e:
                self.lbl_status.configure(text=f"Lỗi khởi tạo hệ thống: {e}", text_color="red")
                
        threading.Thread(target=target, daemon=True).start()

    def filter_voices_by_lang(self, lang_name):
        """Tự động quét và gom toàn bộ giọng Edge-TTS lẫn các giọng đọc mới từ Google."""
        lang_code = self.supported_langs.get(lang_name)
        if not lang_code or not self.raw_voices:
            return

        self.voices_dict = {}

        # 1. Lọc các giọng đọc của Edge-TTS
        for voice in self.raw_voices:
            voice_locale = voice["Locale"].lower()
            voice_lang_prefix = voice_locale.split('-')[0]
            if voice_lang_prefix == lang_code.lower():
                self.voices_dict[voice["FriendlyName"]] = voice["Name"]

        # 2. Nếu là Tiếng Việt, nạp thêm bộ 20 giọng chất lượng cao của Google
        if lang_name == "Tiếng Việt" or lang_code.lower() == "vi":
            google_vietnamese = TTSEngine.get_google_vietnamese_voices()
            self.voices_dict.update(google_vietnamese)

        voice_names = sorted(list(self.voices_dict.keys()))
        self.combo_voice.configure(values=voice_names)
        
        if voice_names:
            self.combo_voice.set(voice_names[0])
            self.lbl_status.configure(
                text=f"Tìm thấy {len(voice_names)} giọng đọc khả dụng cho ngôn ngữ: {lang_name}.", 
                text_color="gray"
            )
        else:
            self.combo_voice.set("Không tìm thấy giọng phù hợp")

    def on_language_change(self, selected_lang):
        self.filter_voices_by_lang(selected_lang)

    def start_translation(self):
        text = self.txt_input.get("0.0", "end").strip()
        if not text or text == "Nhập hoặc dán văn bản gốc vào đây để dịch...":
            messagebox.showwarning("Thông báo", "Vui lòng nhập văn bản gốc ở ô bên trái!")
            return

        target_lang = self.combo_lang.get()
        lang_code = self.supported_langs.get(target_lang)

        if not lang_code:
            messagebox.showerror("Lỗi", "Không xác định được mã ngôn ngữ đích!")
            return

        self.btn_translate.configure(state="disabled", text="⌛ Đang dịch...")
        self.lbl_status.configure(text="Đang kết nối dịch thuật toàn cầu...", text_color="#3498db")

        def target():
            try:
                translated = TTSEngine.translate_text(text, lang_code)
                self.txt_translated.delete("0.0", "end")
                self.txt_translated.insert("0.0", translated)
                self.lbl_status.configure(text="Đã dịch xong! Bạn có thể nghe thử hoặc xuất file MP3.", text_color="#2ecc71")
            except Exception as e:
                messagebox.showerror("Lỗi dịch thuật", f"Có lỗi xảy ra: {e}")
                self.lbl_status.configure(text="Dịch thất bại", text_color="red")
            finally:
                self.btn_translate.configure(state="normal", text="🔄 Dịch văn bản")

        threading.Thread(target=target, daemon=True).start()

    def start_preview(self):
        if self.is_playing_preview:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.btn_preview.configure(text="🔊 Nghe thử bản dịch", fg_color="#2ecc71")
            self.is_playing_preview = False
            self.cleanup_preview_file()
            return

        selected_friendly = self.combo_voice.get()
        voice_id = self.voices_dict.get(selected_friendly)
        text_demo = self.txt_translated.get("0.0", "end").strip()

        if not voice_id or not text_demo or text_demo == "Kết quả dịch sẽ xuất hiện tại đây...":
            messagebox.showwarning("Thông báo", "Chưa có nội dung bản dịch để phát thử!")
            return

        self.btn_preview.configure(text="⌛ Đang tải...", state="disabled")

        def target():
            try:
                import uuid
                self.preview_file_path = f"preview_{uuid.uuid4().hex[:8]}.mp3"
                
                asyncio.run(TTSEngine.preview_voice(text_demo, voice_id, self.preview_file_path))
                
                pygame.mixer.music.load(self.preview_file_path)
                pygame.mixer.music.play()

                self.is_playing_preview = True
                self.btn_preview.configure(text="⏹ Dừng phát", fg_color="#e74c3c", state="normal")

                while pygame.mixer.music.get_busy() and self.is_playing_preview:
                    pygame.time.Clock().tick(10)

            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể phát: {e}")
            finally:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self.cleanup_preview_file()
                self.btn_preview.configure(text="🔊 Nghe thử bản dịch", fg_color="#2ecc71", state="normal")
                self.is_playing_preview = False

        threading.Thread(target=target, daemon=True).start()

    def cleanup_preview_file(self):
        if self.preview_file_path and os.path.exists(self.preview_file_path):
            try:
                os.remove(self.preview_file_path)
                self.preview_file_path = None
            except PermissionError:
                pass

    def update_progress(self, percent, eta_seconds):
        if eta_seconds > 60:
            minutes = eta_seconds // 60
            seconds = eta_seconds % 60
            eta_str = f"{minutes} phút {seconds} giây"
        else:
            eta_str = f"{eta_seconds} giây"

        self.lbl_status.configure(
            text=f"Đang tạo âm thanh... {percent}% | Thời gian còn lại: {eta_str}",
            text_color="#3498db",
        )
        self.progress_bar.set(percent / 100)
        self.update_idletasks()

    def start_conversion(self):
        if self.is_playing_preview:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self.is_playing_preview = False
            self.btn_preview.configure(text="🔊 Nghe thử bản dịch", fg_color="#2ecc71")
            self.cleanup_preview_file()

        text = self.txt_translated.get("0.0", "end").strip()
        selected_friendly = self.combo_voice.get()

        if not text or text == "Kết quả dịch sẽ xuất hiện tại đây...":
            messagebox.showwarning("Thông báo", "Vui lòng nhập và bấm dịch văn bản trước khi xuất MP3!")
            return

        voice_id = self.voices_dict.get(selected_friendly)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3", filetypes=[("MP3 Files", "*.mp3")]
        )

        if file_path:
            self.btn_convert.configure(state="disabled", text="Đang xử lý xuất MP3...")
            self.btn_preview.configure(state="disabled")
            threading.Thread(
                target=self.run_tts, args=(text, voice_id, file_path), daemon=True
            ).start()

    def run_tts(self, text, voice, file_path):
        try:
            asyncio.run(TTSEngine.convert_to_mp3(text, voice, file_path, self.update_progress))
            self.lbl_status.configure(text="Hoàn thành xuất file!", text_color="#2ecc71")
            messagebox.showinfo("Thành công", "Đã xuất file MP3 thành công!")
        except Exception as e:
            self.lbl_status.configure(text="Gặp lỗi xử lý!", text_color="#e74c3c")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
        finally:
            self.btn_convert.configure(state="normal", text="Xuất bản dịch ra file MP3")
            self.btn_preview.configure(state="normal")
            self.progress_bar.set(0)


if __name__ == "__main__":
    app = TTSApp()
    app.mainloop()