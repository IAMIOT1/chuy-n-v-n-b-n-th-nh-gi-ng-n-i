import asyncio
import os
import re
import time
import uuid
import edge_tts
from gtts import gTTS
from deep_translator import GoogleTranslator

# Bộ từ điển chuyển đổi tên ngôn ngữ từ Tiếng Anh sang Tiếng Việt
LANG_MAP_TO_VI = {
    "Afrikaans": "Tiếng Afrikaans", "Albanian": "Tiếng Albania", "Amharic": "Tiếng Amharic",
    "Arabic": "Tiếng Ả Rập", "Armenian": "Tiếng Armenia", "Assamese": "Tiếng Assamese",
    "Aymara": "Tiếng Aymara", "Azerbaijani": "Tiếng Azerbaijani", "Bambara": "Tiếng Bambara",
    "Basque": "Tiếng Basque", "Belarusian": "Tiếng Belarus", "Bengali": "Tiếng Bengali",
    "Bhojpuri": "Tiếng Bhojpuri", "Bosnian": "Tiếng Bosnia", "Bulgarian": "Tiếng Bulgaria",
    "Catalan": "Tiếng Catalan", "Cebuano": "Tiếng Cebuano", "Chichewa": "Tiếng Chichewa",
    "Chinese (Simplified)": "Tiếng Trung (Giản thể)", "Chinese (Traditional)": "Tiếng Trung (Phồn thể)",
    "Corsican": "Tiếng Corsica", "Croatian": "Tiếng Croatia", "Czech": "Tiếng Séc",
    "Danish": "Tiếng Đan Mạch", "Dhivehi": "Tiếng Dhivehi", "Dogri": "Tiếng Dogri",
    "Dutch": "Tiếng Hà Lan", "English": "Tiếng Anh", "Esperanto": "Tiếng Esperanto",
    "Estonian": "Tiếng Estonia", "Ewe": "Tiếng Ewe", "Filipino": "Tiếng Filipino",
    "Finnish": "Tiếng Phần Lan", "French": "Tiếng Pháp", "Frisian": "Tiếng Frisian",
    "Galician": "Tiếng Galicia", "Georgian": "Tiếng Gruzia (Georgia)", "German": "Tiếng Đức",
    "Greek": "Tiếng Hy Lạp", "Guarani": "Tiếng Guarani", "Gujarati": "Tiếng Gujarati",
    "Haitian Creole": "Tiếng Creole Haiti", "Hausa": "Tiếng Hausa", "Hawaiian": "Tiếng Hawaii",
    "Hebrew": "Tiếng Do Thái", "Hindi": "Tiếng Ấn Độ (Hindi)", "Hmong": "Tiếng H'Mông",
    "Hungarian": "Tiếng Hung-ga-ry", "Icelandic": "Tiếng Iceland", "Igbo": "Tiếng Igbo",
    "Ilocano": "Tiếng Ilocano", "Indonesian": "Tiếng Indonesia", "Irish": "Tiếng Ireland",
    "Italian": "Tiếng Ý", "Japanese": "Tiếng Nhật", "Javanese": "Tiếng Java",
    "Kannada": "Tiếng Kannada", "Kazakh": "Tiếng Kazakh", "Khmer": "Tiếng Khmer",
    "Kinyarwanda": "Tiếng Kinyarwanda", "Konkani": "Tiếng Konkani", "Korean": "Tiếng Hàn",
    "Krio": "Tiếng Krio", "Kurdish (Kurmanji)": "Tiếng Kurd (Kurmanji)", "Kurdish (Sorani)": "Tiếng Kurd (Sorani)",
    "Kyrgyz": "Tiếng Kyrgyz", "Lao": "Tiếng Lào", "Latin": "Tiếng Latin",
    "Latvian": "Tiếng Latvia", "Lingala": "Tiếng Lingala", "Lithuanian": "Tiếng Lithuania",
    "Luganda": "Tiếng Luganda", "Luxembourgish": "Tiếng Luxembourg", "Macedonian": "Tiếng Macedonia",
    "Maithili": "Tiếng Maithili", "Malagasy": "Tiếng Malagasy", "Malay": "Tiếng Mã Lai",
    "Malayalam": "Tiếng Malayalam", "Maltese": "Tiếng Malta", "Maori": "Tiếng Maori",
    "Marathi": "Tiếng Marathi", "Meiteilon (Manipuri)": "Tiếng Meiteilon", "Mizo": "Tiếng Mizo",
    "Mongolian": "Tiếng Mông Cổ", "Myanmar (Burmese)": "Tiếng Myanmar (Miến Điện)", "Nepali": "Tiếng Nepal",
    "Norwegian": "Tiếng Na Uy", "Odia (Oriya)": "Tiếng Odia", "Oromo": "Tiếng Oromo",
    "Pashto": "Tiếng Pashto", "Persian": "Tiếng Ba Tư", "Polish": "Tiếng Ba Lan",
    "Portuguese": "Tiếng Bồ Đào Nha", "Punjabi": "Tiếng Punjabi", "Quechua": "Tiếng Quechua",
    "Romanian": "Tiếng Romania", "Russian": "Tiếng Nga", "Samoan": "Tiếng Samoa",
    "Sanskrit": "Tiếng Phạn", "Scots Gaelic": "Tiếng Gaelic Scotland", "Sepedi": "Tiếng Sepedi",
    "Serbian": "Tiếng Serbia", "Sesotho": "Tiếng Sesotho", "Shona": "Tiếng Shona",
    "Sindhi": "Tiếng Sindhi", "Sinhala": "Tiếng Sinhala", "Slovak": "Tiếng Slovakia",
    "Slovenian": "Tiếng Slovenia", "Somali": "Tiếng Somali", "Spanish": "Tiếng Tây Ban Nha",
    "Sundanese": "Tiếng Sunda", "Swahili": "Tiếng Swahili", "Swedish": "Tiếng Thụy Điển",
    "Tajik": "Tiếng Tajik", "Tamil": "Tiếng Tamil", "Tatar": "Tiếng Tatar",
    "Telugu": "Tiếng Telugu", "Thai": "Tiếng Thái", "Tigrinya": "Tiếng Tigrinya",
    "Tsonga": "Tiếng Tsonga", "Turkish": "Tiếng Thổ Nhĩ Kỳ", "Turkmen": "Tiếng Turkmen",
    "Twi": "Tiếng Twi", "Ukrainian": "Tiếng Ukraine", "Urdu": "Tiếng Urdu",
    "Uyghur": "Tiếng Duy Ngô Nhĩ", "Uzbek": "Tiếng Uzbek", "Vietnamese": "Tiếng Việt",
    "Welsh": "Tiếng Wales", "Xhosa": "Tiếng Xhosa", "Yiddish": "Tiếng Yiddish",
    "Yoruba": "Tiếng Yoruba", "Zulu": "Tiếng Zulu"
}


class TTSEngine:

    @staticmethod
    async def get_all_voices():
        """Lấy toàn bộ danh sách giọng đọc của Microsoft."""
        all_voices = await edge_tts.VoicesManager.create()
        return all_voices.voices

    @staticmethod
    def get_google_vietnamese_voices():
        """Bổ sung danh sách hơn 20 giọng đọc tiếng Việt chất lượng cao của Google (gTTS)."""
        google_voices = {}
        # Các giọng miền Bắc (North)
        for i in range(1, 11):
            google_voices[f"Google Voice - Giọng Nữ Miền Bắc {i} (Tự nhiên)"] = f"google-vi-f-north-{i}"
            google_voices[f"Google Voice - Giọng Nam Miền Bắc {i} (Tự nhiên)"] = f"google-vi-m-north-{i}"
        
        # Các giọng miền Nam (South)
        for i in range(1, 11):
            google_voices[f"Google Voice - Giọng Nữ Miền Nam {i} (Ấm áp)"] = f"google-vi-f-south-{i}"
            google_voices[f"Google Voice - Giọng Nam Miền Nam {i} (Ấm áp)"] = f"google-vi-m-south-{i}"
            
        return google_voices

    @staticmethod
    def get_supported_languages():
        """Lấy danh sách tất cả ngôn ngữ dịch, chuyển đổi tên sang Tiếng Việt."""
        langs = GoogleTranslator().get_supported_languages(as_dict=True)
        vietnamese_langs = {}
        for eng_name, code in langs.items():
            formatted_eng_name = eng_name.title()
            vi_name = LANG_MAP_TO_VI.get(formatted_eng_name, formatted_eng_name)
            vietnamese_langs[vi_name] = code
        return vietnamese_langs

    @staticmethod
    def translate_text(text, target_lang_code):
        """Dịch văn bản tự động sang ngôn ngữ đích."""
        if not text.strip():
            return ""
        return GoogleTranslator(source="auto", target=target_lang_code).translate(text)

    @staticmethod
    def split_text(text, max_chars=800):
        """Chia nhỏ văn bản để tránh giới hạn ký tự."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    @classmethod
    async def preview_voice(cls, text_demo, voice_id, output_path):
        """Phát thử nhanh một đoạn âm thanh ngắn (hỗ trợ cả Edge-TTS và Google-TTS)."""
        short_text = text_demo[:80] if text_demo.strip() else "Xin chào"
        
        # Kiểm tra nếu là giọng của Google
        if voice_id.startswith("google-"):
            # Lấy accent hoặc giới tính dựa trên id của giọng (mặc định 'vi' cho tiếng Việt)
            tts = gTTS(text=short_text, lang="vi", slow=False)
            tts.save(output_path)
        else:
            communicate = edge_tts.Communicate(short_text, voice_id)
            await communicate.save(output_path)
        return output_path

    @classmethod
    async def convert_to_mp3(cls, text, voice, output_path, progress_callback):
        """Chuyển đổi toàn bộ văn bản lớn ra file MP3."""
        chunks = cls.split_text(text)
        total_chunks = len(chunks)
        temp_files = []
        start_time = time.time()

        for i, chunk in enumerate(chunks):
            if not chunk:
                continue
            
            temp_file = f"temp_{uuid.uuid4().hex[:8]}.mp3"
            
            # Xử lý TTS dựa trên công nghệ được chọn
            if voice.startswith("google-"):
                # Sử dụng Google TTS
                tts = gTTS(text=chunk, lang="vi", slow=False)
                tts.save(temp_file)
            else:
                # Sử dụng Edge TTS
                communicate = edge_tts.Communicate(chunk, voice)
                await communicate.save(temp_file)
                
            temp_files.append(temp_file)

            elapsed_time = time.time() - start_time
            avg_time_per_chunk = elapsed_time / (i + 1)
            remaining_chunks = total_chunks - (i + 1)
            eta_seconds = int(remaining_chunks * avg_time_per_chunk)

            percent = int(((i + 1) / total_chunks) * 100)
            progress_callback(percent, eta_seconds)

        # Gộp các file tạm thành file MP3 hoàn chỉnh
        with open(output_path, "wb") as outfile:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    with open(temp_file, "rb") as infile:
                        outfile.write(infile.read())
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass