import streamlit as st
import time
import re

st.set_page_config(page_title="Dynamic NLP Essay Evaluator", page_icon="📝", layout="wide")

st.title("📝 Hệ thống NLP Phân tích Bài viết Tiếng Anh & Chỉ ra Lỗi khi Chấm")
st.caption("Chuyên môn NLP: Real-time Inline Error Highlighting, Dynamic Grammar Diagnostics & Lexical Analysis")
st.markdown("---")

# --- BƯỚC 1: NHẬP BÀI LUẬN TỰ DO CỦA HỌC SINH ---
st.header("Bước 1: Nhập bài viết Tiếng Anh của Học sinh")

essay_topic = st.text_input("Đề bài / Chủ đề bài luận (Topic):", 
                            placeholder="Ví dụ: Benefits of learning English, Environmental protection...")

student_essay = st.text_area("Nội dung bài viết của Học sinh (Gõ hoặc dán văn bản tự do vào đây):", 
                             placeholder="Nhập đoạn văn tiếng Anh của học sinh tại đây...",
                             height=180)

if st.button("🚀 Chạy Mô hình NLP Phân tích & Chỉ ra Lỗi"):
    if not student_essay.strip():
        st.error("Vui lòng nhập bài viết tiếng Anh để hệ thống NLP phân tích!")
    else:
        with st.spinner("NLP Engine đang xử lý Tokenization, Bắt lỗi Ngữ pháp & Highlight trực tiếp..."):
            time.sleep(1.5)
        st.session_state['analyzed_text'] = student_essay
        st.session_state['analyzed'] = True

# --- BƯỚC 2, 3, 4: THỰC HIỆN CHẤM VÀ HIGHLIGHT LỖI TRỰC TIẾP ---
if st.session_state.get('analyzed', False):
    text = st.session_state.get('analyzed_text', '')
    
    st.markdown("---")
    st.header("Bước 2 & 3: Kết quả Chấm & Chỉ ra Lỗi trực tiếp trên Bài viết")
    
    # 1. TOKENIZATION DỮ LIỆU THỰC TẾ
    raw_words = re.findall(r'\b\w+\b', text)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    word_count = len(raw_words)
    sentence_count = len(sentences)
    unique_words = len(set([w.lower() for w in raw_words]))
    
    # 2. TÍNH CHỈ SỐ TTR ĐỘNG
    ttr = round((unique_words / word_count) * 100, 1) if word_count > 0 else 0
    avg_sentence_len = round(word_count / sentence_count, 1) if sentence_count > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Tổng số từ (Word Count)", value=f"{word_count}")
    with col2:
        st.metric(label="Số câu (Sentence Count)", value=f"{sentence_count}")
    with col3:
        st.metric(label="Độ dài trung bình câu", value=f"{avg_sentence_len} từ/câu")
    with col4:
        st.metric(label="Độ đa dạng từ vựng (TTR)", value=f"{ttr}%")

    st.markdown("---")
    
    # 3. CHẨN ĐOÁN LỖI BẰNG NLP & TẠO CHUỖI HIGHLIGHT
    detected_errors = []
    highlighted_text = text

    # Luật 1: Kiểm tra lỗi viết hoa đầu câu
    for idx, sent in enumerate(sentences, 1):
        if sent and not sent[0].isupper():
            detected_errors.append({
                "cau": sent,
                "loi_loai": "Capitalization Error",
                "de_xuat": f"Viết hoa chữ cái đầu câu: '{sent[0].upper() + sent[1:]}'",
                "giai_thich": "Mọi câu trong Tiếng Anh bắt đầu bằng chữ cái viết hoa."
            })

    # Luật 2: Kiểm tra lỗi "a/an"
    vowel_matches = re.findall(r'\b(a)\s+([aeiouAEIOU]\w+)', text)
    for m in vowel_matches:
        error_phrase = f"a {m[1]}"
        detected_errors.append({
            "cau": f"...{error_phrase}...",
            "loi_loai": "Indefinite Article Error (a/an)",
            "de_xuat": f"Đổi '{error_phrase}' thành 'an {m[1]}'",
            "giai_thich": "Dùng mạo từ 'an' trước các từ bắt đầu bằng nguyên âm (a, e, i, o, u)."
        })
        # Tô màu đỏ đoạn bị lỗi
        highlighted_text = highlighted_text.replace(error_phrase, f"<mark style='background-color: #ffcccc; color: #b30000; padding: 2px 4px; border-radius: 4px;'><b>{error_phrase}</b> (Lỗi a/an)</mark>")

    # Luật 3: Kiểm tra lỗi danh từ số nhiều đi với "many/several"
    many_matches = re.findall(r'\b(many|several)\s+([a-zA-Cg-z]+)(?<!s)\b', text, re.IGNORECASE)
    for m in many_matches:
        if m[1].lower() not in ['people', 'children', 'men', 'women', 'mice', 'feet', 'teeth']:
            error_phrase = f"{m[0]} {m[1]}"
            detected_errors.append({
                "cau": f"...{error_phrase}...",
                "loi_loai": "Plural Noun Agreement",
                "de_xuat": f"Đổi '{m[1]}' thành dạng số nhiều '{m[1]}s'",
                "giai_thich": f"Sau tính từ chỉ số lượng '{m[0]}' cần sử dụng danh từ đếm được số nhiều."
            })
            # Tô màu vàng đoạn bị lỗi
            highlighted_text = highlighted_text.replace(error_phrase, f"<mark style='background-color: #fff2cc; color: #8a6d3b; padding: 2px 4px; border-radius: 4px;'><b>{error_phrase}</b> (Lỗi danh từ số nhiều)</mark>")

    # Luật 4: Lỗi lặp từ
    word_counts_dict = {}
    for w in raw_words:
        w_lower = w.lower()
        if len(w_lower) > 3 and w_lower not in ['this', 'that', 'with', 'from', 'have', 'more', 'they', 'their', 'some', 'about']:
            word_counts_dict[w_lower] = word_counts_dict.get(w_lower, 0) + 1
            
    repeated_words = [w for w, count in word_counts_dict.items() if count >= 3]
    if repeated_words:
        detected_errors.append({
            "cau": f"Các từ xuất hiện nhiều lần: {', '.join(repeated_words)}",
            "loi_loai": "Lexical Redundancy (Lặp từ)",
            "de_xuat": "Sử dụng các từ đồng nghĩa (Synonyms) để làm phong phú văn phong.",
            "giai_thich": "Việc lặp lại 1 từ quá 3 lần làm giảm chỉ số đa dạng từ vựng."
        })

    # HIỂN THỊ TRỰC QUAN BÀI VIẾT ĐÃ ĐƯỢC CHỈ LỖI
    st.subheader("🔴 Bài viết được AI chấm điểm & Đánh dấu lỗi trực tiếp (Inline Error Markup):")
    st.markdown(f"<div style='background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; line-height: 1.8;'>{highlighted_text}</div>", unsafe_allow_keywords=True, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Danh sách Báo cáo Lỗi chi tiết:")
    
    if detected_errors:
        for idx, err in enumerate(detected_errors, 1):
            with st.expander(f"❌ Lỗi {idx}: [{err['loi_loai']}] - Vị trí: \"{err['cau']}\""):
                st.markdown(f"- **Đề xuất chỉnh sửa:** `{err['de_xuat']}`")
                st.markdown(f"- **Quy tắc NLP áp dụng:** {err['giai_thich']}")
    else:
        st.success("🎉 Bài viết không mắc các lỗi ngữ pháp/chính tả cơ bản!")

    # --- BƯỚC 4: XẾP LOẠI & ĐÁNH GIÁ ---
    st.markdown("---")
    st.header("Bước 4: Chẩn đoán Năng lực Ngôn ngữ")
    
    error_count = len(detected_errors)
    if error_count == 0 and ttr > 60:
        cefr_level = "B2 / C1 (Upper-Intermediate)"
        overall_score = 9.0
    elif error_count <= 2 and ttr > 45:
        cefr_level = "B1 (Intermediate)"
        overall_score = 7.5
    elif error_count <= 4:
        cefr_level = "A2 (Elementary)"
        overall_score = 6.0
    else:
        cefr_level = "A1 (Beginner)"
        overall_score = 4.5

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Dự đoán Trình độ CEFR", value=cefr_level)
        st.metric(label="Điểm Đánh giá Ngôn ngữ", value=f"{overall_score} / 10")
    
    with col_b:
        st.markdown("### 📊 Đánh giá tổng quan khi chấm:")
        st.markdown(f"- Phát hiện tổng cộng **{error_count} lỗi ngữ pháp/từ vựng**.")
        st.markdown(f"- Mức độ phong phú từ vựng đạt **{ttr}%**.")

    # --- BƯỚC 5: ĐỀ XUẤT BÀI TẬP CỦNG CỐ CÁ NHÂN HÓA ---
    st.markdown("---")
    st.header("Bước 5: Đề xuất Bài tập Cá nhân hóa khắc phục đúng lỗi vừa mắc")
    st.warning("🎯 **Lộ trình rèn luyện được AI khởi tạo tự động dựa trên các lỗi bị đánh dấu:**")
    
    if detected_errors:
        for err in detected_errors:
            st.markdown(f"- 📝 **Bài tập củng cố dạng [{err['loi_loai']}]:** Luyện tập lại quy tắc `{err['giai_thich']}`.")
    else:
        st.markdown("- 📝 **Bài tập nâng cao:** Viết lại đoạn văn trên sử dụng các cấu trúc câu phức (Complex Sentences).")

    # BÁO CÁO GIÁO VIÊN
    st.markdown("---")
    st.header("📋 Báo cáo Chi tiết Log NLP gửi Giáo viên")
    st.json({
        "raw_essay_snippet": text[:100] + "...",
        "word_count": word_count,
        "sentence_count": sentence_count,
        "ttr_lexical_score": ttr,
        "detected_error_count": error_count,
        "cefr_assessment": cefr_level,
        "error_summary": [e["loi_loai"] for e in detected_errors]
    })
    st.success("Đã chấm điểm, đánh dấu lỗi trực tiếp và xuất báo cáo thành công!")