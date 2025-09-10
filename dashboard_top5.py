import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.title("Dashboard Doanh thu BHX")

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
col1, col2 = st.columns(2)

with col1:
    am_list = sorted(df["AM"].dropna().unique())
    am_chon = st.multiselect("Chọn AM", options=am_list, default=am_list[:1])

df_am = df[df["AM"].isin(am_chon)] if am_chon else df.copy()

with col2:
    sieuthi_list = sorted(df_am["Mã siêu thị"].dropna().unique())
    sieuthi_chon = st.multiselect(
        "Chọn Siêu thị",
        options=sieuthi_list,
        default=sieuthi_list[:1] if sieuthi_list else []
    )

# Lọc dữ liệu cuối cùng
df_filtered = df_am[df_am["Mã siêu thị"].isin(sieuthi_chon)] if sieuthi_chon else df_am.copy()

#===================================

# Lọc dữ liệu tháng 8 trong file dthuthang.xlsx
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
today = datetime.date.today()
ngay = today.day

if ngay > 1:
    doanhthu_du_kien = doanhthu_hientai / (ngay - 1) * 30
else:
    doanhthu_du_kien = doanhthu_hientai

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Doanh thu đến hiện tại", f"{doanhthu_hientai:,.0f}")
with col2:
    st.metric("Dự kiến tháng 9", f"{doanhthu_du_kien:,.0f}")
with col3:
    st.metric("Doanh thu T8", f"{tong_doanhthu_t8:,.0f}")

#================================

# === Biểu đồ tròn FMCG vs Fresh ===
st.subheader("Cơ cấu Doanh thu FMCG vs Fresh")

tong_doanhthu_nh = (
    df_filtered.groupby("NH")[["Tổng doanh thu"]]
    .sum()
    .reset_index()
) 

if ngay > 1:
    tong_doanhthu_nh["Dự kiến T9"] = (tong_doanhthu_nh["Tổng doanh thu"] / (ngay - 1) * 30).round(0)
else:
    tong_doanhthu_nh["Dự kiến T9"] = tong_doanhthu_nh["Tổng doanh thu"]

tong_all = tong_doanhthu_nh["Tổng doanh thu"].sum()
tong_doanhthu_nh["Tỉ trọng (%)"] = (tong_doanhthu_nh["Tổng doanh thu"] / tong_all * 100).round(2)

fig_pie = px.pie(
    tong_doanhthu_nh,
    names="NH",
    values="Tổng doanh thu",
    title="Cơ cấu Doanh thu FMCG vs Fresh",
    hole=0.3
)

st.plotly_chart(fig_pie, use_container_width=True)
st.dataframe(
    tong_doanhthu_nh.style.format({"Tổng doanh thu": "{:,.0f}","Dự kiến T9": "{:,.0f}","Tỉ trọng (%)": "{:,.2f}"})
)

#===================================
 
col1, col2 = st.columns(2)

# === Top 10 Nhóm hàng ===
with col1:
    st.subheader("Top 10 Nhóm hàng doanh thu cao nhất")

    tong_doanhthu = df_filtered["Tổng doanh thu"].sum()

    top10_nhomhang = (
        df_filtered.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .head(10)
        .reset_index()
    )

    top10_nhomhang["Tỉ trọng (%)"] = (top10_nhomhang["Tổng doanh thu"] / tong_doanhthu * 100).round(2)

    fig = px.bar(
        top10_nhomhang,
        x="Nhóm hàng",
        y="Tổng doanh thu",
        text_auto=".2s",
        title="Top 10 Nhóm hàng doanh thu cao nhất",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        top10_nhomhang.style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )

# === Top 10 Nhóm hàng FMCG ===
with col2:
    st.subheader("Top 10 Nhóm hàng (FMCG) doanh thu cao nhất")

    df_fmcg = df_filtered[df_filtered["NH"] == "FMCG"]
    tong_doanhthu_fmcg = df_fmcg["Tổng doanh thu"].sum()

    top10_fmcg = (
        df_fmcg.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .head(10)
        .reset_index()
    )

    top10_fmcg["Tỉ trọng (%)"] = (top10_fmcg["Tổng doanh thu"] / tong_doanhthu_fmcg * 100).round(2)

    fig_fmcg = px.bar(
        top10_fmcg,
        x="Nhóm hàng",
        y="Tổng doanh thu",
        text_auto=".2s",
        title="Top 10 Nhóm hàng (FMCG) doanh thu cao nhất",
        height=500
    )
    st.plotly_chart(fig_fmcg, use_container_width=True)

    st.dataframe(
        top10_fmcg.style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )
