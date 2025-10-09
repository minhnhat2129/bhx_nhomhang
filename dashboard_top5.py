import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.title(f"📊 Dashboard Doanh thu BHX")

#---------------------- upload


#----------------------

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

PASSWORD="BHX123"

#* password_input = st.text_input("Nhập mật khẩu để truy cập:", type="password")

#if password_input != PASSWORD:
  #  st.warning("Vui lòng nhập đúng mật khẩu để xem nội dung 🚫")
 #   st.stop()   # Dừng lại, không chạy các phần dưới
#else:
 #   st.success("")
    # ======= Toàn bộ code dashboard của bạn đặt dưới đây =======
#    st.write()

# === Load dữ liệu gốc và mapping ===
df = pd.read_excel("dthumodel.xlsx")
#dthu_thang9 = pd.read_excel("dthut9.xlsx")
mapping = pd.read_excel("mapping_NH.xlsx")
dthu_thang8 = pd.read_excel("dthuthang.xlsx")

# Chuẩn hóa tên cột
df.columns = df.columns.str.strip()
mapping.columns = mapping.columns.str.strip()
dthu_thang8.columns = dthu_thang8.columns.str.strip()

# Merge để lấy cột NH (FMCG, Fresh, Đông mát...)
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
st.header(f"Doanh thu BHX {sieuthi_chon}")
# Lọc dữ liệu cuối cùng
df_filtered = df_am[df_am["Mã siêu thị"].isin(sieuthi_chon)] if sieuthi_chon else df_am.copy()

# ===================================
# Mapping doanh thu T8 từ file dthuthang.xlsx
if sieuthi_chon:
    doanhthu_t8 = (
        dthu_thang8[
            (dthu_thang8["Mã siêu thị"].isin(sieuthi_chon))
        ]["Tổng doanh thu"].sum() 
    )
else:
    doanhthu_t8 = (
        dthu_thang8[
            (dthu_thang8["Tháng"] == "T8") &
            (dthu_thang8["AM"].isin(am_chon))
        ]["Tổng doanh thu"].sum()
    )

# Tính KPI
doanhthu_hientai = df_filtered["Tổng doanh thu"].sum() 

today = datetime.date.today()
ngay = today.day 

if ngay > 1:
    doanhthu_du_kien = doanhthu_hientai / (ngay - 1) * 30 
else:
    doanhthu_du_kien = doanhthu_hientai 

#def format_vnd(value):
 #   # Làm tròn về triệu
  #  value = round(value, -6)  
   # ty = value // 1_000_000_000
    #trieu = (value % 1_000_000_000) // 1_000_000

    #if ty > 0 and trieu > 0:
     #   return f"{ty} tỉ {trieu} triệu"
    #elif ty > 0:
     #   return f"{ty} tỉ"
    #else:
     #   return f"{trieu} triệu"

def format_vnd(value: int) -> str:
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f} Tỉ".rstrip("0").rstrip(".")
    elif value >= 1_000_000:
        return f"{value/1_000_000:.0f} Triệu"
    else:
        return f"{value/1_000_000:,.0f} Triệu"  # trường hợp nhỏ hơn 1 triệu
     
    
tangtruong_t8 = ( (doanhthu_du_kien / (doanhthu_t8)) - 1 ) * 100
tanggiam = doanhthu_du_kien - doanhthu_t8

dthutbngay = doanhthu_hientai / (ngay - 1)
dthutbngaythangtruoc = doanhthu_t8 / 31
tanggiamtbngay = dthutbngay - dthutbngaythangtruoc


# === Hiển thị KPI ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Doanh thu đến hiện tại", format_vnd(doanhthu_hientai))
with col2:
    st.metric("Dự kiến hết tháng", format_vnd(doanhthu_du_kien), delta=format_vnd(tanggiam))
with col3:
    st.metric("Tăng trưởng so tháng trước", f"{tangtruong_t8:.1f}%", delta=f"{tangtruong_t8:.1f}%")
with col4:
    st.metric("Doanh thu trung bình ngày", format_vnd(dthutbngay), delta=format_vnd(tanggiamtbngay))
        



    
#================================


# === Biểu đồ tròn FMCG vs Fresh ===
st.subheader("🥧 Cơ cấu Doanh thu FMCG vs Fresh")

tong_doanhthu_nh = (
    df_filtered.groupby("NH")[["Tổng doanh thu"]]
    .sum()
    .reset_index()
) 

if ngay > 1:
    tong_doanhthu_nh["Dự kiến T9"] = (tong_doanhthu_nh["Tổng doanh thu"] / (ngay - 1) * 30).round(0)
else:
    tong_doanhthu_nh["Dự kiến T9"] = tong_doanhthu_nh["Tổng doanh thu"]

# Tính tỉ trọng
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
 
# Chia layout 2 cột
col1, col2 = st.columns(2)

# === Top 10 Nhóm hàng ===
with col1:
    st.subheader("🔝 Top 10 Nhóm hàng doanh thu cao nhất")

    tong_doanhthu = df_filtered["Tổng doanh thu"].sum()

    top10_nhomhang = (
        df_filtered.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .head(10)
        .reset_index()
    )

    # Thêm cột tỉ trọng
    top10_nhomhang["Tỉ trọng (%)"] = (top10_nhomhang["Tổng doanh thu"] / tong_doanhthu * 100).round(2)

    # Vẽ biểu đồ
    fig = px.bar(
        top10_nhomhang,
        x="Nhóm hàng",
        y="Tổng doanh thu",
        text_auto=".2s",
        title="Top 10 Nhóm hàng doanh thu cao nhất",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Hiển thị bảng chi tiết
    st.dataframe(
        top10_nhomhang.style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )


# === Top 10 Nhóm hàng FMCG ===
with col2:
    st.subheader("🔝 Top 10 Nhóm hàng (FMCG) doanh thu cao nhất")

    df_fmcg = df_filtered[df_filtered["NH"] == "FMCG"]

    tong_doanhthu_fmcg = df_fmcg["Tổng doanh thu"].sum()

    top10_fmcg = (
        df_fmcg.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .head(10)
        .reset_index()
    )

    # Thêm tỉ trọng trong FMCG
    top10_fmcg["Tỉ trọng (%)"] = (top10_fmcg["Tổng doanh thu"] / tong_doanhthu_fmcg * 100).round(2)

    # Vẽ biểu đồ
    fig_fmcg = px.bar(
        top10_fmcg,
        x="Nhóm hàng",
        y="Tổng doanh thu",
        text_auto=".2s",
        title="Top 10 Nhóm hàng (FMCG) doanh thu cao nhất",
        height=500
    )
    st.plotly_chart(fig_fmcg, use_container_width=True)

    # Hiển thị bảng
    st.dataframe(
        top10_fmcg.style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )



#=======================================================================

# Chia bố cục 2 cột
col1, col2 = st.columns(2)

# === Top 5 Model trong Top 10 Nhóm hàng FMCG ===
with col2:
    st.subheader("⭐ Top 5 Model bán tốt nhất trong 10 Nhóm hàng FMCG")

    # Lấy danh sách 10 nhóm hàng FMCG
    list_top10_fmcg = top10_fmcg["Nhóm hàng"].tolist()
    df_top10_fmcg = df_fmcg[df_fmcg["Nhóm hàng"].isin(list_top10_fmcg)]

    # Tính tổng doanh thu và số lượng theo model
    top5_models_fmcg = (
        df_top10_fmcg.groupby(["Nhóm hàng", "Model"])[["Tổng doanh thu", "Tổng số lượng"]]
        .sum()
        .reset_index()
    )

    # Lấy top 5 model theo doanh thu trong từng nhóm hàng
    result_fmcg = (
        top5_models_fmcg
        .sort_values(["Nhóm hàng", "Tổng doanh thu"], ascending=[True, False])
        .groupby("Nhóm hàng")
        .head(5)
        .reset_index(drop=True)
    )

    # Sắp xếp nhóm hàng theo tổng doanh thu giảm dần
    nhomhang_order_fmcg = (
        df_top10_fmcg.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .reset_index()
    )

    result_fmcg = result_fmcg.merge(nhomhang_order_fmcg, on="Nhóm hàng", suffixes=("", "_nhom"))
    result_fmcg = result_fmcg.sort_values(["Tổng doanh thu_nhom", "Tổng doanh thu"], ascending=[False, False])

    # Hiển thị bảng
    st.dataframe(
        result_fmcg[["Nhóm hàng", "Model", "Tổng doanh thu", "Tổng số lượng"]]
        .style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tổng số lượng": "{:,.0f}"
        })
    )


# === Top 5 Model trong Top 10 Nhóm hàng ===
with col1:
    st.subheader("⭐ Top 5 Model trong 10 Nhóm hàng doanh thu cao nhất")

    list_top10 = top10_nhomhang["Nhóm hàng"].tolist()
    df_top10 = df_filtered[df_filtered["Nhóm hàng"].isin(list_top10)]

    top5_models_per_group = (
        df_top10.groupby(["Nhóm hàng", "Model"])[["Tổng doanh thu", "Tổng số lượng"]]
        .sum()
        .reset_index()
    )

    result = (
        top5_models_per_group
        .sort_values(["Nhóm hàng", "Tổng doanh thu"], ascending=[True, False])
        .groupby("Nhóm hàng")
        .head(5)
        .reset_index(drop=True)
    )

    # Thứ tự nhóm hàng theo tổng doanh thu
    nhomhang_order = (
        df_top10.groupby("Nhóm hàng")[["Tổng doanh thu"]] 
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .reset_index()
    )

    result = result.merge(nhomhang_order, on="Nhóm hàng", suffixes=("", "_nhom"))
    result = result.sort_values(["Tổng doanh thu_nhom", "Tổng doanh thu"], ascending=[False, False])

    st.dataframe(
        result[["Nhóm hàng", "Model", "Tổng doanh thu", "Tổng số lượng"]]
        .style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tổng số lượng": "{:,.0f}"
        })
    )


#=============================================================================

col1, col2 = st.columns(2)

# === Top 10 Nhóm hàng ĐÔNG MÁT ===
with col1:
    st.subheader("🔝 Top 10 Nhóm hàng (ĐÔNG MÁT) theo doanh thu")

    df_dm = df_filtered[df_filtered["NH"] == "ĐÔNG MÁT"]

    tong_doanhthu_dm = df_dm["Tổng doanh thu"].sum()

    top10_dm = (
        df_dm.groupby("Nhóm hàng")[["Tổng doanh thu"]]
        .sum()
        .sort_values("Tổng doanh thu", ascending=False)
        .head(10)
        .reset_index()
    )

    # Thêm tỉ trọng
    top10_dm["Tỉ trọng (%)"] = (top10_dm["Tổng doanh thu"] / tong_doanhthu_dm * 100).round(2)

    # Vẽ biểu đồ
    fig_dm = px.bar(
        top10_dm,
        x="Nhóm hàng",
        y="Tổng doanh thu",
        text_auto=".2s",
        title="Top 10 Nhóm hàng (ĐÔNG MÁT)",
        height=500
    )
    st.plotly_chart(fig_dm, use_container_width=True)

    # Hiển thị bảng
    st.dataframe(
        top10_dm.style.format({
            "Tổng doanh thu": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )


# === Top 10 Nhóm hàng FRESH ===
with col2:
    st.subheader("🔝 Top 10 Nhóm hàng (FRESH) theo sản lượng")

    df_fr = df_filtered[df_filtered["NH"] == "FRESH"]

    tong_sl_fr = df_fr["Tổng số lượng"].sum()

    top10_fr = (
        df_fr.groupby("Nhóm hàng")[["Tổng số lượng"]]
        .sum()
        .sort_values("Tổng số lượng", ascending=False)
        .head(10)
        .reset_index()
    )

    # Thêm tỉ trọng
    top10_fr["Tỉ trọng (%)"] = (top10_fr["Tổng số lượng"] / tong_sl_fr * 100).round(2)

    # Vẽ biểu đồ
    fig_fr = px.bar(
        top10_fr,
        x="Nhóm hàng",
        y="Tổng số lượng",
        text_auto=".2s",
        title="Top 10 Nhóm hàng (FRESH)",
        height=500
    )
    st.plotly_chart(fig_fr, use_container_width=True)

    # Hiển thị bảng
    st.dataframe(
        top10_fr.style.format({
            "Tổng số lượng": "{:,.0f}",
            "Tỉ trọng (%)": "{:,.2f}"
        })
    )
