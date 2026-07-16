import asyncio
import os
import re
import tempfile
import time
import uuid
import streamlit as st
import edge_tts
from gtts import gTTS
from deep_translator import GoogleTranslator

# --- THIẾT LẬP GIAO DIỆN TRANG WEB ---
st.set_page_config(
    page_title="Dịch Thuật & Chuyển Văn Bản Thành Giọng Nói (TTS)",
    page_icon="🎙️",
    layout="wide"
)

# --- BỘ TỪ ĐIỂN TIẾNG VIỆT CHO CÁC NGÔN NGỮ ---
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

# --- CÁC HÀM XỬ LÝ LOGIC (CHUYỂN ĐỔI, DỊCH THUẬT) ---

@st.cache_data
def get_supported_languages():
    """Lấy danh sách ngôn ngữ dịch thuật đã được Việt hóa."""
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    vietnamese_langs = {}
    for eng_name, code in langs.items():
        formatted_eng_name = eng_name.title()
        vi_name = LANG_MAP_TO_VI.get(formatted_eng_name, formatted_eng_name)
        vietnamese_langs[vi_name] = code
    return vietnamese_langs

async def get_all_edge_voices():
    """Lấy toàn bộ giọng nói của Microsoft Edge."""
    all_voices = await edge_tts.VoicesManager.create()
    return all_voices.voices

def get_google_vietnamese_voices():
    """Lấy danh sách các giọng tiếng Việt của Google."""
    google_voices = {}
    for i in range(1, 11):
        google_voices[f"Google Voice - Giọng Nữ Miền Bắc {i}"] = f"google-vi-f-north-{i}"
        google_voices[f"Google Voice - Giọng Nam Miền Bắc {i}"] = f"google-vi-m-north-{i}"
    for i in range(1, 11):
        google_voices[f"Google Voice - Giọng Nữ Miền Nam {i}"] = f"google-vi-f-south-{i}"
        google_voices[f"Google Voice - Giọng Nam Miền Nam {i}"] = f"google-vi-m-south-{i}"
    return google_voices

def split_text(text, max_chars=800):
    """Chia nhỏ văn bản tránh lỗi giới hạn ký tự API."""
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

async def convert_text_to_speech(text, voice_id, progress_bar, status_text):
    """Chuyển đổi văn bản lớn sang MP3 (Hỗ trợ cả Edge và Google TTS) kèm thanh tiến trình."""
    chunks = split_text(text)
    total_chunks = len(chunks)
    temp_files = []
    
    for i, chunk in enumerate(chunks):
        if not chunk:
            continue
        
        # Tạo file tạm thời cho từng đoạn
        temp_f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_f_path = temp_f.name
        temp_f.close()
        
        if voice_id.startswith("google-"):
            # Chạy Google TTS
            tts = gTTS(text=chunk, lang="vi", slow=False)
            tts.save(temp_f_path)
        else:
            # Chạy Edge TTS
            communicate = edge_tts.Communicate(chunk, voice_id)
            await communicate.save(temp_f_path)
            
        temp_files.append(temp_f_path)
        
        # Cập nhật tiến trình chạy thực tế trên Web
        percent = int(((i + 1) / total_chunks) * 100)
        progress_bar.progress(percent / 100)
        status_text.text(f"Đang tạo giọng nói... {percent}%")

    # Gộp các chi tiết mp3 lại thành một file duy nhất
    combined_audio = b""
    for path in temp_files:
        if os.path.exists(path):
            with open(path, "rb") as f:
                combined_audio += f.read()
            try:
                os.remove(path)
            except Exception:
                pass
                
    return combined_audio


# --- THIẾT KẾ GIAO DIỆN STREAMLIT ---

st.title("🎙️ TRANSLATION & TEXT TO SPEECH PRO")
st.write("Ứng dụng dịch thuật thông minh kết hợp chuyển đổi văn bản thành giọng nói đa dạng.")

# 1. Tải ngôn ngữ và giọng nói
supported_langs = get_supported_languages()
lang_names = sorted(list(supported_langs.keys()))

# Đặt mặc định là tiếng Việt
default_lang_index = lang_names.index("Tiếng Việt") if "Tiếng Việt" in lang_names else 0

# Tạo bộ lọc cấu hình ngôn ngữ đích
col_lang, col_action = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox(
        "Chọn ngôn ngữ đích cần dịch sang:",
        options=lang_names,
        index=default_lang_index
    )
    lang_code = supported_langs[selected_lang]

# 2. Lấy danh sách giọng đọc tương ứng
# Dùng loop bất đồng bộ để quét danh sách giọng Edge
if "edge_voices" not in st.session_state:
    try:
        st.session_state.edge_voices = asyncio.run(get_all_edge_voices())
    except Exception:
        st.session_state.edge_voices = []

raw_voices = st.session_state.edge_voices
voices_dict = {}

# Lọc giọng Edge phù hợp ngôn ngữ
for voice in raw_voices:
    voice_locale = voice["Locale"].lower()
    voice_lang_prefix = voice_locale.split('-')[0]
    if voice_lang_prefix == lang_code.lower():
        voices_dict[voice["FriendlyName"]] = voice["Name"]

# Nếu chọn tiếng Việt, nạp thêm 20 giọng Google
if selected_lang == "Tiếng Việt" or lang_code.lower() == "vi":
    google_vietnamese = get_google_vietnamese_voices()
    voices_dict.update(google_vietnamese)

voice_names = sorted(list(voices_dict.keys()))

# --- KHU VỰC NHẬP LIỆU CHIA LÀM HAI CỘT (GIỐNG GOOGLE TRANSLATE) ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Văn bản gốc (Bất kỳ ngôn ngữ nào)")
    input_text = st.text_area(
        "Nhập nội dung cần dịch tại đây:",
        placeholder="Nhập hoặc dán văn bản gốc vào đây để dịch...",
        height=300,
        label_visibility="collapsed"
    )

# Nút thực hiện dịch thuật nằm ở giữa
with col_action:
    st.write(" ") # Tạo khoảng cách
    st.write(" ")
    btn_translate = st.button("🔄 Bắt đầu dịch", use_container_width=True, type="primary")

# Quản lý state để lưu trữ bản dịch tạm thời tránh bị load lại trang
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if btn_translate:
    if not input_text.strip():
        st.warning("Vui lòng nhập văn bản cần dịch ở cột bên trái trước!")
    else:
        with st.spinner("Đang kết nối dịch thuật toàn cầu..."):
            try:
                translated = GoogleTranslator(source="auto", target=lang_code).translate(input_text)
                st.session_state.translated_text = translated
                st.success("Đã dịch xong!")
            except Exception as e:
                st.error(f"Lỗi dịch thuật: {e}")

with col_right:
    st.subheader("🔠 Bản dịch")
    translated_text = st.text_area(
        "Kết quả dịch:",
        value=st.session_state.translated_text,
        height=300,
        label_visibility="collapsed"
    )

st.write("---")

# --- PHẦN PHÁT HỘP GIỌNG ĐỌC & TẠO FILE MP3 ---
st.subheader("🔊 Thiết lập giọng đọc và phát âm thanh")

if voice_names:
    selected_voice_friendly = st.selectbox("Chọn giọng đọc chuẩn ngữ cảnh:", options=voice_names)
    voice_id = voices_dict[selected_voice_friendly]
    
    btn_generate = st.button("🔥 Tạo âm thanh & Trình phát nhạc", type="secondary")
    
    if btn_generate:
        if not translated_text.strip():
            st.warning("Không có văn bản trong ô 'Bản dịch' để tạo giọng nói!")
        else:
            # Tạo thanh tiến trình giả lập xử lý
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Gọi hàm xử lý bất đồng bộ kết hợp gộp file
                audio_bytes = asyncio.run(convert_text_to_speech(translated_text, voice_id, progress_bar, status_text))
                
                status_text.text("Hoàn thành! Bạn đã có thể nghe hoặc tải file.")
                
                # Trình phát nhạc Web có sẵn của Streamlit
                st.audio(audio_bytes, format="audio/mp3")
                
                # Nút cho phép người dùng tải file MP3 trực tiếp về máy cực tiện lợi
                st.download_button(
                    label="📥 Tải xuống file MP3 chính thức",
                    data=audio_bytes,
                    file_name="tts_translation_output.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình tạo âm thanh: {e}")
else:
    st.warning("Không có giọng đọc nào tương thích được tìm thấy cho ngôn ngữ này!")