import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.title(f"📊 Dashboard Doanh thu BHX")

#---------------------- upload

st.title("📂 Upload dữ liệu")

# Ô chọn file
uploaded_file = st.file_uploader("Chọn file Excel hoặc CSV", type=["xlsx", "csv"])

# Nút upload
if uploaded_file is not None:
    if st.button("📥 Upload file"):
        file_path = uploaded_file.name  # Lưu ngay cùng thư mục với code
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File đã được lưu vào: {os.path.abspath(file_path)}")

        # Xem thử dữ liệu nếu là Excel/CSV
        try:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)

            st.write("📊 Xem trước dữ liệu:")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Lỗi khi đọc file: {e}")
