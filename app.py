import streamlit as st
import pandas as pd
import time

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม (ปรับขนาดตัวหนังสือให้ใหญ่ อ่านง่ายสำหรับชาวนา)
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; }
    .stButton>button { width: 100%; font-size: 20px !important; height: 50px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบจำลองฐานข้อมูล (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}

# --- แถบเมนูด้านล่าง (Bottom Navigation จำลองด้วย Sidebar เพื่อความง่าย) ---
st.sidebar.image("https://flaticon.com", width=100)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")
st.sidebar.write("ระบบรับซื้อ-ขายข้าวและบริการเกษตร")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard)", "📋 รายการของฉัน", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🏠 เมนู: หน้าแรก
# =========================================================================
if menu == "🏠 หน้าแรก (Dashboard)":
    st.markdown('<p class="big-font">🌾 ราคารับซื้อข้าวประจำวัน อ.โนนสูง</p>', unsafe_allow_html=True)
    
    # จำลองตารางราคากลาง
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="price-box">
            <b>🌾 ข้าวหอมมะลิ 105</b><br>
            <span style="font-size: 22px; color: #E65100;"><b>14,500 - 15,200</b></span> บาท/ตัน<br>
            <small>*ความชื้นไม่เกิน 15%</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="price-box">
            <b>🌾 ข้าวเจ้าทั่วไป</b><br>
            <span style="font-size: 22px; color: #E65100;"><b>10,200 - 10,800</b></span> บาท/ตัน<br>
            <small>*ความชื้นไม่เกิน 15%</small>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    # ปุ่มฟีเจอร์หลัก
    st.markdown('<p class="big-font">🟢 ทำรายการ</p>', unsafe_allow_html=True)
    
    # ระบบกรอกข้อมูลเพื่อขายข้าว
    with st.expander("💰 กดที่นี่เพื่อสั่งขายข้าวเปลือก", expanded=False):
        st.subheader("กรอกข้อมูลข้าวของคุณ")
        rice_type = st.selectbox("ประเภทข้าว", ["ข้าวหอมมะลิ 105", "ข้าวเจ้าทั่วไป"])
        amount = st.number_input("ปริมาณโดยประมาณ (ตัน)", min_value=0.1, max_value=100.0, value=5.0, step=0.5)
        moisture = st.slider("คาดการณ์ความชื้น (%)", 10, 30, 15)
        
        st.subheader("📌 พิกัดนัดหมายรับข้าว")
        sub_district = st.selectbox("ตำบล (ในอำเภอโนนสูง)", ["โนนสูง", "ใหม่", "โตนด", "จันอัด", "ด่านคล้า", "ขามสะแกแสง"])
        gps_mock = st.text_input("พิกัดนาข้าว (จำลอง GPS)", "15.1814° N, 102.2531° E (ทุ่งนาโนนสูง)")
        
        if st.button("🚀 ยืนยันการส่งข้อมูลขายข้าว"):
            st.session_state.order_status = "โรงสีกำลังเสนอราคา"
            st.session_state.order_detail = {
                "ประเภท": rice_type,
                "ปริมาณ": amount,
                "ความชื้น": moisture,
                "พื้นที่": f"ต.{sub_district} อ.โนนสูง"
            }
            st.success("ส่งข้อมูลสำเร็จ! ระบบกำลังจับคู่โรงสีที่ให้ราคาดีที่สุดให้คุณ")
            st.balloons()

    # บริการในอนาคต (เฟส 2)
    st.write("---")
    st.markdown('<p class="big-font">🚀 บริการอื่นๆ (เร็วๆ นี้)</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🛒 ซื้อปุ๋ย/เมล็ดพันธุ์ (จ่ายทีหลัง)", disabled=True)
    with c2:
        st.button("🛸 จองโดรนพ่นยา / รถเกี่ยว", disabled=True)

# =========================================================================
# 📋 เมนู: รายการของฉัน
# =========================================================================
elif menu == "📋 รายการของฉัน":
    st.markdown('<p class="big-font">📋 สถานะการขายข้าวของคุณ</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("คุณยังไม่มีรายการขายข้าวในขณะนี้ กลับไปที่หน้าแรกเพื่อส่งข้อมูล")
    else:
        st.write(f"**🌾 สินค้า:** ข้าว{st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ ปริมาณ:** {st.session_state.order_detail['ปริมาณ']} ตัน (ความชื้นประมาณ {st.session_state.order_detail['ความชื้น']}% )")
        st.write(f"**📍 สถานที่:** {st.session_state.order_detail['พื้นที่']}")
        
        # แสดงสถานะแบบ Timeline
        status = st.session_state.order_status
        st.warning(f"🔔 สถานะปัจจุบัน: **{status}**")
        
        # ปุ่มจำลองเปลี่ยนสถานะหน้างานเพื่อให้เห็น Workflow
        if status == "โรงสีกำลังเสนอราคา":
            if st.button("อนุมัติราคาจาก โรงสีโนนสูงเจริญการค้า (15,000 บ./ตัน)"):
                st.session_state.order_status = "รถขนส่งกำลังเดินทางไปแปลงนา"
                st.rerun()
        elif status == "รถขนส่งกำลังเดินทางไปแปลงนา":
            if st.button("จำลอง: รถมาถึงแล้ว ชั่งน้ำหนักและโอนเงิน"):
                st.session_state.order_status = "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)"
                st.rerun()
        elif status == "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)":
            st.success("🎉 การซื้อขายเสร็จสิ้นสมบูรณ์ ชาวนาได้รับเงินเรียบร้อย!")
            if st.button("เริ่มรายการใหม่"):
                st.session_state.order_status = "ยังไม่มีรายการ"
                st.rerun()
