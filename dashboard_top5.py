import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.title("📊 Dashboard Doanh thu BHX")

# === Load dữ liệu gốc và mapping ===
df = pd.read_excel("dthumodel.xlsx")
mapping = pd.read_excel("mapping_NH.xlsx")
dthu_thang8 = pd.read_excel("dthuthang.xlsx")

# Chuẩn hóa tên cột
df.columns = df.columns.str.strip()
mapping.columns = mapping.columns.str.strip()
dthu_thang8.columns = dthu_thang8.columns.str.strip()

# Merge để lấy cột NH (FMCG vs Fresh)
df = df.merge(mapping, on="Ngành hàng", how="left")

# === Bộ lọc AM & Siêu thị ===
st.sidebar.header("🔎 Bộ lọc dữ liệu")

am_list = sorted(df["AM"].dropna().unique())
am_chon = st.sidebar.multiselect("Chọn AM", options=am_list, default=am_list[:1])
df_am = df[df["AM"].isin(am_chon)] if am_chon else df.copy()

sieuthi_list = sorted(df_am["Mã siêu thị"].dropna().unique())
sieuthi_chon = st.sidebar.multiselect(
    "Chọn Siêu thị",
    options=sieuthi_list,
    default=sieuthi_list[:1] if sieuthi_list else []
)

df_filtered = df_am[df_am["Mã siêu thị"].isin(sieuthi_chon)] if sieuthi_chon else df_am.copy()

# === Doanh thu tháng 8 ===
doanhthu_t8 = dthu_thang8[dthu_thang8["Tháng"] == "T8"].copy()
doanhthu_t8 = doanhthu_t8.rename(columns={"Tổng doanh thu": "Doanh thu T8"})
df_kpi = df_filtered.merge(
    doanhthu_t8[["Mã siêu thị", "Doanh thu T8"]],
    on="Mã siêu thị",
    how="left"
)
tong_doanhthu_t8 = df_kpi["Doanh thu T8"].sum()

# === KPI ===
doanhthu_hientai = df_filtered["Tổng doanh thu"].sum()
ngay = datetime.date.today().day
doanhthu_du_kien = doanhthu_hientai / max(1, ngay - 1) * 30

st.markdown("### 📈 KPI Doanh thu")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("💰 Doanh thu hiện tại", f"{doanhthu_hientai:,.0f}")
kpi2.metric("📅 Dự kiến T9", f"{doanhthu_du_kien:,.0f}")
kpi3.metric("📅 Doanh thu T8", f"{tong_doanhthu_t8:,.0f}")

# === Biểu đồ tròn FMCG vs Fresh ===
st.markdown("### 🥧 Cơ cấu Doanh thu FMCG vs Fresh")

tong_doanhthu_nh = (
    df_filtered.groupby("NH")[["Tổng doanh thu"]]
    .sum()
    .reset_index()
)
tong_doanhthu_nh["Tỉ trọng (%)"] = (
    tong_doanhthu_nh["Tổng doanh thu"] / tong_doanhthu_nh["Tổng doanh thu"].sum() * 100
).round(2)

fig_pie = px.pie(
    tong_doanhthu_nh,
    names="NH",
    values="Tổng doanh thu",
    hole=0.3,
    height=350
)
st.plotly_chart(fig_pie, use_container_width=True)
st.dataframe(
    tong_doanhthu_nh.style.format({
        "Tổng doanh thu": "{:,.0f}",
        "Tỉ trọng (%)": "{:,.2f}"
    }),
    height=250
)

# === Top 10 Nhóm hàng ===
st.markdown("### 🔝 Top 10 Nhóm hàng theo Doanh thu")
top10_nhomhang = (
    df_filtered.groupby("Nhóm hàng")[["Tổng doanh thu"]]
    .sum()
    .sort_values("Tổng doanh thu", ascending=False)
    .head(10)
    .reset_index()
)
fig_top10 = px.bar(
    top10_nhomhang,
    x="Nhóm hàng",
    y="Tổng doanh thu",
    text_auto=".2s",
    height=350
)
st.plotly_chart(fig_top10, use_container_width=True)
st.dataframe(top10_nhomhang.style.format({"Tổng doanh thu": "{:,.0f}"}), height=250)
