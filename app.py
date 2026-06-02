import streamlit as st
import pandas as pd

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    .calc-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-top: 15px; }
    .stButton>button { width: 100%; font-size: 20px !important; height: 50px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ข้อมูลราคากลางฐาน (ความชื้นมาตรฐาน 10%) ---
BASE_PRICES = {
    "ข้าวหอมมะลิ 105": 18200.0,  # บาทต่อตัน
    "ข้าวเจ้าทั่วไป": 10500.0     # บาทต่อตัน
}

# --- ระบบจำลองฐานข้อมูล (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}

# --- แถบเมนูด้านล่าง (Sidebar สำหรับ Prototype) ---
st.sidebar.image("https://flaticon.com", width=100)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")
st.sidebar.write("ระบบรับซื้อ-ขายข้าวและบริการเกษตร")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard)", "📋 รายการของฉัน", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🏠 เมนู: หน้าแรก
# =========================================================================
if menu == "🏠 หน้าแรก (Dashboard)":
    st.markdown('<p class="big-font">🌾 ราคารับซื้อข้าวเกณฑ์มาตรฐาน อ.โนนสูง</p>', unsafe_allow_html=True)
    st.write("*ราคาอ้างอิงความชื้นมาตรฐานไม่เกิน 15%*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="price-box">
            <b>🌾 ข้าวหอมมะลิ 105</b><br>
            <span style="font-size: 22px; color: #2E7D32;"><b>{BASE_PRICES['ข้าวหอมมะลิ 105']:,}</b></span> บาท/ตัน
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="price-box">
            <b>🌾 ข้าวเจ้าทั่วไป</b><br>
            <span style="font-size: 22px; color: #2E7D32;"><b>{BASE_PRICES['ข้าวเจ้าทั่วไป']:,}</b></span> บาท/ตัน
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    # 🧮 ฟีเจอร์ใหม่: ระบบคำนวณราคากลางข้าวตามความชื้น
    st.markdown('<p class="big-font">🧮 เครื่องคำนวณราคากลางตามความชื้น</p>', unsafe_allow_html=True)
    
    calc_rice_type = st.selectbox("1. เลือกประเภทข้าวที่ต้องการคำนวณ", list(BASE_PRICES.keys()), key="calc_type")
    calc_amount = st.number_input("2. ใส่ปริมาณข้าว (ตัน)", min_value=0.1, max_value=100.0, value=1.0, step=0.5, key="calc_weight")
    calc_moisture = st.slider("3. ปรับเปอร์เซ็นต์ความชื้น (%)", min_value=11, max_value=30, value=15, key="calc_moist")
    
    # สูตรคำนวณ: ถ้าความชื้นเกิน 15% หักตันละ 150 บาท ต่อความชื้นที่เกินทุกๆ 1%
    base_price_per_ton = BASE_PRICES[calc_rice_type]
    deduction_per_percent = 150.0  # ค่ามาตรฐานโรงสีหักความชื้น
    
    if calc_moisture > 15:
        moisture_over = calc_moisture - 15
        final_price_per_ton = base_price_per_ton - (moisture_over * deduction_per_percent)
        note_text = f"⚠️ ถูกหักค่าความชื้นเกินมา {moisture_over}% (หักตันละ {moisture_over * deduction_per_percent:,} บาท)"
    elif calc_moisture < 15:
        # ข้าวแห้งกว่ามาตรฐาน บางลานข้าวอาจจะให้ราคาเพิ่มขึ้นเล็กน้อย หรือคงราคาเดิม (ในที่นี้ให้ราคาเพิ่มตันละ 50 บาท)
        moisture_less = 15 - calc_moisture
        final_price_per_ton = base_price_per_ton + (moisture_less * 50.0)
        note_text = "✨ ข้าวแห้งดี ได้ราคาดีเป็นพิเศษ"
    else:
        final_price_per_ton = base_price_per_ton
        note_text = "✅ ความชื้นตามเกณฑ์มาตรฐานพอดี"
        
    total_money = final_price_per_ton * calc_amount
    
    # แสดงผลลัพธ์การคำนวณให้ชาวนาเห็นชัดๆ
    st.markdown(f"""
    <div class="calc-box">
        <span style="font-size: 16px; color: #555;">💰 ราคาประเมินสุทธิที่คุณจะได้รับ:</span><br>
        <span style="font-size: 32px; color: #E65100;"><b>{total_money:,} บาท</b></span><br>
        <small>คิดเป็นเฉลี่ยตันละ: {final_price_per_ton:,} บาท ({note_text})</small>
    </div>
    """, unsafe_allow_html=True)
        
    st.write("---")
    
    # ปุ่มส่งข้อมูลขายข้าว
    st.markdown('<p class="big-font">🟢 ส่งข้อมูลเสนอขายข้าว</p>', unsafe_allow_html=True)
    
    with st.expander("คลิกที่นี่เพื่อส่งข้อมูลให้โรงสีในโนนสูงติดต่อกลับ"):
        sub_district = st.selectbox("ตำบลของคุณ (ในอำเภอโนนสูง)", ["โนนสูง", "ใหม่", "โตนด", "จันอัด", "ด่านคล้า", "ขามสะแกแสง"])
        gps_mock = st.text_input("พิกัดแปลงนา (จำลอง GPS)", "15.1814° N, 102.2531° E (ทุ่งนาโนนสูง)")
        
        if st.button("🚀 ยืนยันการส่งข้อมูลขายข้าว"):
            st.session_state.order_status = "โรงสีกำลังเสนอราคา"
            st.session_state.order_detail = {
                "ประเภท": calc_rice_type,
                "ปริมาณ": calc_amount,
                "ความชื้น": calc_moisture,
                "ราคาประเมิน": total_money,
                "พื้นที่": f"ต.{sub_district} อ.โนนสูง"
            }
            st.success("ส่งข้อมูลสำเร็จ! ระบบกำลังส่งข้อมูลให้โรงสีใกล้เคียงเพื่อประมูลราคา")
            st.balloons()

# =========================================================================
# 📋 เมนู: รายการของฉัน
# =========================================================================
elif menu == "📋 รายการของฉัน":
    st.markdown('<p class="big-font">📋 สถานะการขายข้าวของคุณ</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("คุณยังไม่มีรายการขายข้าวในขณะนี้ กลับไปที่หน้าแรกเพื่อส่งข้อมูล")
    else:
        st.write(f"**🌾 สินค้า:** ข้าว{st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ ปริมาณ:** {st.session_state.order_detail['ปริมาณ']} ตัน (ความชื้น {st.session_state.order_detail['ความชื้น']}% )")
        st.write(f"**💰 ราคาประเมินเบื้องต้น:** {st.session_state.order_detail['ราคาประเมิน']:,} บาท")
        st.write(f"**📍 สถานที่:** {st.session_state.order_detail['พื้นที่']}")
        
        status = st.session_state.order_status
        st.warning(f"🔔 สถานะปัจจุบัน: **{status}**")
        
        if status == "โรงสีกำลังเสนอราคา":
            if st.button("อนุมัติราคาจาก โรงสีโนนสูงเจริญการค้า"):
                st.session_state.order_status = "รถขนส่งกำลังเดินทางไปแปลงนา"
                st.rerun()
        elif status == "รถขนส่งกำลังเดินทางไปแปลงนา":
            if st.button("จำลอง: รถมาถึงแล้ว ชั่งน้ำหนักจริงตรงตามแอป และโอนเงิน"):
                st.session_state.order_status = "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)"
                st.rerun()
        elif status == "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)":
            st.success("🎉 การซื้อขายเสร็จสิ้นสมบูรณ์ ชาวนาได้รับเงินเรียบร้อย!")
            if st.button("เริ่มรายการใหม่"):
                st.session_state.order_status = "ยังไม่มีรายการ"
                st.rerun()

# =========================================================================
# เมนูอื่นๆ คงเดิมเพื่อความเสถียร
# =========================================================================
elif menu == "💬 กล่องข้อความ":
    st.markdown('<p class="big-font">💬 แชทติดต่อสอบถาม</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.write("**👨‍🌾 คุณ (ชาวนา):** สวัสดีครับ รถขนส่งจะเข้ามากี่โมงครับ?")
        st.write("**🏭 โรงสีโนนสูงเจริญการค้า:** กำลังจัดคิวรถออกไปช่วงบ่ายโมงวันนี้ครับพ่อใหญ่ เตรียมหน้าแปลงนาไว้ได้เลยจ้า")
    st.text_input("พิมพ์ข้อความของคุณที่นี่...")
    st.button("ส่งข้อความ")

elif menu == "👤 ข้อมูลส่วนตัว":
    st.markdown('<p class="big-font">👤 ข้อมูลเกษตรกร</p>', unsafe_allow_html=True)
    st.text_input("ชื่อ - นามสกุล", value="นายสมศักดิ์ รักบ้านเกิด")
    st.text_input("เลขทะเบียนเกษตรกร (ทบก.)", value="1-3004-XXXXX-XX-X")
    st.subheader("🏦 บัญชีธนาคารสำหรับรับเงินค่าข้าว")
    st.text_input("ธนาคาร", value="ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (ธ.ก.ส.)")
    st.text_input("เลขที่บัญชี / PromptPay", value="020-1-XXXXX-X")
    st.button("บันทึกข้อมูลส่วนตัว")
