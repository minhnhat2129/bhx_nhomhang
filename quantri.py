import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Doanh thu", layout="wide")
st.header("📊BÁO CÁO DOANH THU MIỀN RSM TRUNG ĐỨC")


st.markdown("""
    <style>
    .block-container {padding-top: 3rem; padding-bottom: 1rem;}
    .stMetric {background-color: #f9f9f9; border-radius: 10px; padding: 10px;font-color:red;}
    .font-color:red
    </style>
""", unsafe_allow_html=True)
#---------------------- upload

#st.title("📂 Upload dữ liệu")

# Ô chọn file
#uploaded_file = st.file_uploader("Chọn file Excel hoặc CSV", type=["xlsx", "csv"])

# Nút upload
#if uploaded_file is not None:
#    if st.button("📥 Upload file"):
#        file_path = uploaded_file.name  # Lưu ngay cùng thư mục với code
#        with open(file_path, "wb") as f:
#            f.write(uploaded_file.getbuffer())

#        st.success(f"✅ File đã được lưu vào: {os.path.abspath(file_path)}")

        # Xem thử dữ liệu nếu là Excel/CSV
#        try:
#            if uploaded_file.name.endswith(".xlsx"):
#                df = pd.read_excel(file_path)
#            else:
#                df = pd.read_csv(file_path)

#            st.write("📊 Xem trước dữ liệu:")
#            st.dataframe(df.head())
#        except Exception as e:
#            st.error(f"Lỗi khi đọc file: {e}")

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

# =================gọi hàm================

#chuẩn tỉ, triệu
def format_vnd(value: int) -> str:
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f} Tỉ".rstrip("0").rstrip(".")
    elif value >= 1_000_000:
        return f"{value/1_000_000:.0f} Triệu"
    else:
        return f"{value/1_000_000:,.0f} Triệu"  # trường hợp nhỏ hơn 1 triệu


# Tính số ngày trong tháng
so_ngay_trong_thang = {
    1: 31,
    2: 28,   # nếu cần tính năm nhuận thì xử lý riêng
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


#--------kết thúc gọi hàm

# === Load dữ liệu gốc và mapping ===
df = pd.read_excel("dthu1den9.xlsx")
#dthu_thang9 = pd.read_excel("dthut9.xlsx")
mapping = pd.read_excel("mapping_am_mst.xlsx")
dthu_thang8 = pd.read_excel("dthuthang.xlsx")

# Chuẩn hóa tên cột
df.columns = df.columns.str.strip()
mapping.columns = mapping.columns.str.strip()
dthu_thang8.columns = dthu_thang8.columns.str.strip()

# Merge để lấy cột NH (FMCG, Fresh, Đông mát...)
df = df.merge(mapping[["Mã siêu thị", "MST", "AM2"]], on="Mã siêu thị", how="left")

# === Bộ lọc AM, Siêu thị (MST), Tháng ===
col1, col2 = st.columns(2)

with col1:
    am_list = sorted(df["AM"].dropna().unique())
    am_chon = st.multiselect(
        "Chọn QLTP",
        options=am_list,
        default=am_list[:1] if am_list else []
    )

df_am = df[df["AM"].isin(am_chon)] if am_chon else df.copy()

with col2:
    sieuthi_list = sorted(df_am["Tên siêu thị"].dropna().unique())
    sieuthi_chon = st.multiselect(
        "Chọn Siêu thị",
        options=sieuthi_list,
        default=sieuthi_list[:1] if sieuthi_list else []
    )

df_sieuthi = df_am[df_am["Tên siêu thị"].isin(sieuthi_chon)] if sieuthi_chon else df_am.copy()
st.subheader(f"Báo cáo doanh thu siêu thị {sieuthi_chon}")

#with col3:
 #   thang_list = sorted(df_sieuthi["Tháng"].dropna().unique())
  #  thang_chon = st.multiselect(
   #     "Chọn Tháng",
    #    options=thang_list,
     #   default=thang_list[:1] if thang_list else []
    #)

# === Lọc dữ liệu cuối cùng ===
#df_filtered = df_sieuthi[df_sieuthi["Tháng"].isin(thang_chon)] if thang_chon else df_sieuthi.copy()
df_filtered = df_sieuthi[df_sieuthi["Tháng"] == "T9"]







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






     
# Tính KPI
today = datetime.date.today()
ngay = today.day
thang = today.month
thang_truoc = thang - 1
so_ngay_thang_hientai = so_ngay_trong_thang[thang]

so_ngay_thang_truoc = so_ngay_trong_thang[thang-1]


doanhthu_hientai = df_filtered["Tổng doanh thu"].sum() 
doanhthu_t8 = df_sieuthi[df_sieuthi["Tháng"] == "T8"]["Tổng doanh thu"].sum()
bill_t8 = df_sieuthi[df_sieuthi["Tháng"] == "T8"]["Tổng số bill"].sum()

bill_hientai = df_filtered["Tổng số bill"].sum()
bill_tb_t9 = bill_hientai / (ngay - 1)
bill_du_kien = bill_hientai / (ngay - 1) * 30 


 

if ngay > 1:
    doanhthu_du_kien = doanhthu_hientai / (ngay - 1) * 30 
else:
    doanhthu_du_kien = doanhthu_hientai
    
tangtruong_t8 = ( (doanhthu_du_kien / (doanhthu_t8)) - 1 ) * 100
tanggiam = doanhthu_du_kien - doanhthu_t8

tanggiam_bill = (bill_du_kien - bill_t8) / 30

dthutbngay = doanhthu_hientai / (ngay - 1)
dthutbngaythangtruoc = doanhthu_t8 / 31
tanggiamtbngay = dthutbngay - dthutbngaythangtruoc



songay = so_ngay_trong_thang[3]


# === Hiển thị KPI ===
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Doanh thu đến hiện tại", format_vnd(doanhthu_hientai))
with col2:
    st.metric("Dự kiến hết tháng", format_vnd(doanhthu_du_kien))
with col3:
    st.metric("Tăng trưởng so tháng trước", f"{tangtruong_t8:.1f}%", delta=format_vnd(tanggiam))
with col4:
    st.metric("Doanh thu trung bình/ngày", format_vnd(dthutbngay), delta=format_vnd(tanggiamtbngay))
with col5:
    st.metric("Lượt bill trung bình/ngày", f"{bill_tb_t9:,.0f} Bill", delta=f"{tanggiam_bill:.0f} bill")


#tinh tổng
def tong_tb(cot_tinh: str, tinh_tb_ngay=False):
    """
    Group theo 'Tháng' và tính tổng cho cột được chọn
    Nếu tinh_tb_ngay=True thì chia cho số ngày trong tháng để ra trung bình/ngày
    Riêng tháng hiện tại thì chia cho số ngày đã trôi qua (today.day - 1)
    """
    today = datetime.date.today()
    thang_hientai = today.month
    ngay_hientai = today.day

    df_sum = df_sieuthi.groupby("Tháng", as_index=False)[cot_tinh].sum()

    if tinh_tb_ngay:
        def tinh_songay(row):
            thang = int(row["Tháng"].replace("T", ""))
            if thang == thang_hientai:
                return max(1, ngay_hientai - 1)  # tránh chia 0
            else:
                return so_ngay_trong_thang[thang]

        df_sum["Số ngày"] = df_sum.apply(tinh_songay, axis=1)
        df_sum[f"{cot_tinh} TB/ngày"] = (df_sum[cot_tinh] / df_sum["Số ngày"]).round(0)

    return df_sum

def tong_dukien(cot_tinh: str, tinh_tb_ngay=False):

     # Bảng số ngày trong từng tháng
    so_ngay_trong_thang = {
        1: 31, 2: 28, 3: 31, 4: 30,
        5: 31, 6: 30, 7: 31, 8: 31,
        9: 30, 10: 31, 11: 30, 12: 31
    }
    
    today = datetime.date.today()
    thang_hientai = today.month
    ngay_hientai = today.day

    df_sum = df_sieuthi.groupby("Tháng", as_index=False)[cot_tinh].sum()

    # Thêm cột dự kiến
    df_sum[f"{cot_tinh} dự kiến"] = None

    for i, row in df_sum.iterrows():
        thang = int(row["Tháng"].replace("T", ""))
        tong_thang = row[cot_tinh]

        if thang < thang_hientai:  
            df_sum.at[i, f"{cot_tinh} dự kiến"] = tong_thang

        elif thang == thang_hientai:
            songay_tinh = max(1, ngay_hientai - 1)  # tránh chia 0
            du_kien = tong_thang / songay_tinh * so_ngay_trong_thang[thang_hientai]
            df_sum.at[i, f"{cot_tinh} dự kiến"] = round(du_kien, 0)

        else:
            df_sum.at[i, f"{cot_tinh} dự kiến"] = None

    # Ép kiểu về số (float), tránh lỗi object dtype
    df_sum[f"{cot_tinh} dự kiến"] = pd.to_numeric(df_sum[f"{cot_tinh} dự kiến"], errors="coerce")

    return df_sum
    

#bieudo_thang = (
#    df_sieuthi.groupby("Tháng", as_index=False)["Tổng doanh thu"].sum()
#)

# Giả sử bạn có biến doanh thu dự kiến T9
du_kien_t9 = doanhthu_du_kien   # thay bằng số thực tế






col11, col12 = st.columns(2)

with col11:

    # Bar chart: doanh thu theo tháng
    bieudo_thang = tong_dukien("Tổng doanh thu")


    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bieudo_thang["Tháng"],
        y=bieudo_thang["Tổng doanh thu dự kiến"]/1e9,  # đổi sang Tỷ VND
        text=(bieudo_thang["Tổng doanh thu dự kiến"]/1e9).round(1),
        textposition="outside",
        marker=dict(color="#33CCFF"),
        name="Doanh thu"
    ))

    fig.update_layout(
        title="📊 Doanh thu theo Tháng",
        yaxis_title="Doanh thu (Tỷ VND)",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

#--------------

with col12:
    # Bar chart: bill TB ngày
    bieudo_bill = tong_tb("Tổng số bill", tinh_tb_ngay=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bieudo_bill["Tháng"],
        y=bieudo_bill["Tổng số bill TB/ngày"],
        text=bieudo_bill["Tổng số bill TB/ngày"],
        textposition="top center",   # hiển thị số trên điểm
        mode="lines+markers+text",   # line + marker + text
        line=dict(color="LimeGreen", width=4),
        marker=dict(size=12),
        name="Số bill"
    ))

    fig.update_layout(
        title="📈 Số bill TB/Ngày",
        yaxis_title="Số bill",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)


    

#===========


col21, col22 = st.columns(2)

with col21:

     # Bar chart: doanh thu tb ngay
    bieudo_thang = tong_tb("Tổng doanh thu",tinh_tb_ngay=True)


    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bieudo_thang["Tháng"],
        y=bieudo_thang["Tổng doanh thu TB/ngày"] / 1e6,  # đổi sang Triệu VND
        mode="lines+markers+text",  # thêm "text" để hiển thị giá trị
        fill="tozeroy",  # tạo vùng màu dưới đường
        line=dict(color="#FF9966", width=3),
        marker=dict(size=8, color="#FF6600"),
        text=(bieudo_thang["Tổng doanh thu TB/ngày"] / 1e6).round(1),
        textposition="bottom center",  # vị trí hiển thị trên marker
        name="Doanh thu TB/Ngày"
    ))

    fig.update_layout(
        title="📈 Doanh thu TB/Ngày theo Tháng",
        yaxis_title="Doanh thu (Triệu VND)",
        height=500,
        margin=dict(l=30, r=30, t=30, b=30),
        plot_bgcolor="white",
        paper_bgcolor="red",
        xaxis=dict(
            showgrid=False,
            linecolor="#ccc",
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eee",
            zeroline=False,
            tickfont=dict(size=12)
        )
    )

     
    st.plotly_chart(fig, use_container_width=True)





#===============




with col22:

    # Bar chart: bill TB ngày
    bieudo_bill = tong_tb("Tổng số bill online", tinh_tb_ngay=True)
    bieudo_doanhthu = tong_tb("Doanh thu online", tinh_tb_ngay=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bieudo_doanhthu["Tháng"],
        y=bieudo_doanhthu["Doanh thu online TB/ngày"] / 1e6,  # đổi triệu VND
        text=(bieudo_doanhthu["Doanh thu online TB/ngày"] / 1e6).round(1),
        textposition="outside",
        marker=dict(color="#FFCC00"),
        name="Doanh thu online TB/ngày",
        yaxis="y1"
        ))

    # --- Line chart: Số bill online TB/ngày ---
    fig.add_trace(go.Scatter(
        x=bieudo_bill["Tháng"],
        y=bieudo_bill["Tổng số bill online TB/ngày"],
        text=bieudo_bill["Tổng số bill online TB/ngày"],
        textposition="bottom center",
        mode="lines+markers+text",
        line=dict(color="#EE6363", width=3),
        marker=dict(size=8),
        name="Số bill online TB/ngày",
        yaxis="y2"
    ))

    # --- Layout ---
    fig.update_layout(
        title="📊 Doanh thu Online và SL đơn Online (TB/Ngày/Tháng)",
        xaxis=dict(title="Tháng"),
        yaxis=dict(
            title="Doanh thu online (Triệu VND)",
            side="left"
        ),
        yaxis2=dict(
            title="Số bill online",
            overlaying="y",
            side="right"
        ),
        height=500,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)
   

#--------------


