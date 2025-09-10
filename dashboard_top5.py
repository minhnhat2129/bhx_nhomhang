import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# ===============================
# Cấu hình trang
# ===============================
st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.title("📊 Dashboard Doanh thu theo Ngành hàng & Model")

# ===============================
# Load dữ liệu
# ===============================
file_path = "dthumodel.xlsx"   # 👉 thay bằng tên file dữ liệu
df = pd.read_excel(file_path)

# Chuẩn hóa tên cột
df.columns = df.columns.str.strip()

# ===============================
# Bộ lọc
# ===============================
col1, col2 = st.columns(2)

with col1:
    am_list = sorted(df["AM"].dropna().unique())
    am_chon = st.multiselect("Chọn AM", options=am_list, default=am_list)

df_am = df[df["AM"].isin(am_chon)] if am_chon else df.copy()

with col2:
    sieuthi_list = sorted(df_am["Mã siêu thị"].dropna().unique())
    sieuthi_chon = st.multiselect("Chọn Siêu thị", options=sieuthi_list, default=sieuthi_list)

df_filtered = df_am[df_am["Mã siêu thị"].isin(sieuthi_chon)] if sieuthi_chon else df_am.copy()

# === KPI dòng 1 & 2 ===
doanhthu_hientai = df_filtered["Tổng doanh thu"].sum()

today = datetime.date.today()
ngay = today.day

if ngay > 1:
    doanhthu_du_kien = doanhthu_hientai / (ngay - 1) * 30
else:
    doanhthu_du_kien = doanhthu_hientai

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Doanh thu đến hiện tại", f"{doanhthu_hientai:,.0f}")
with col2:
    st.metric("📅 Dự kiến tháng 9", f"{doanhthu_du_kien:,.0f}")

# ===============================
# Biểu đồ cột: Tổng doanh thu theo Ngành hàng
# ===============================
doanhthu_nganhhang = (
    df_filtered.groupby("Ngành hàng")[["Tổng doanh thu"]]
    .sum()
    .sort_values("Tổng doanh thu", ascending=False)
    .reset_index()
)

fig = px.bar(
    doanhthu_nganhhang,
    x="Ngành hàng",
    y="Tổng doanh thu",
    title="Tổng doanh thu theo Ngành hàng",
    text_auto=".2s"   # hiển thị gọn: 1.2M, 500K
)
fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    yaxis=dict(title="Tổng doanh thu", tickformat=",")
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# Top 10 nhóm hàng có doanh thu cao nhất
# ===============================
st.subheader("🔝 Top 10 Nhóm hàng có doanh thu cao nhất")

top10_nhomhang = (
    df_filtered.groupby("Nhóm hàng")[["Tổng doanh thu"]]
    .sum()
    .sort_values("Tổng doanh thu", ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(
    top10_nhomhang.style.format({"Tổng doanh thu": "{:,.0f}"})
)

# ===============================
# Top 5 model của 10 nhóm hàng trên
# ===============================
st.subheader("⭐ Top 5 Model bán tốt nhất trong 10 Nhóm hàng")

list_top10 = top10_nhomhang["Nhóm hàng"].tolist()
df_top10 = df_filtered[df_filtered["Nhóm hàng"].isin(list_top10)]

# Tính doanh thu theo Model
top5_models_per_group = (
    df_top10.groupby(["Nhóm hàng", "Mã Model", "Model"])[["Tổng doanh thu", "Tổng số lượng"]]
    .sum()
    .reset_index()
)

# Lấy top 5 model theo doanh thu trong từng nhóm hàng
result = (
    top5_models_per_group
    .sort_values(["Nhóm hàng", "Tổng doanh thu"], ascending=[True, False])
    .groupby("Nhóm hàng")
    .head(5)
    .reset_index(drop=True)
)

# === Thêm tổng doanh thu nhóm hàng để sắp xếp ===
nhomhang_order = (
    df_top10.groupby("Nhóm hàng")[["Tổng doanh thu"]]
    .sum()
    .sort_values("Tổng doanh thu", ascending=False)
    .reset_index()
)

# Merge để biết thứ tự nhóm hàng
result = result.merge(nhomhang_order, on="Nhóm hàng", suffixes=("", "_nhom"))

# Sort theo tổng doanh thu nhóm hàng (cao → thấp)
result = result.sort_values(["Tổng doanh thu_nhom", "Tổng doanh thu"], ascending=[False, False])

# Hiển thị
st.dataframe(
    result[["Nhóm hàng", "Mã Model", "Model", "Tổng doanh thu", "Tổng số lượng"]]
    .style.format({
        "Tổng doanh thu": "{:,.0f}",
        "Tổng số lượng": "{:,.0f}"
    })
)
