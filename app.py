import streamlit as st
import pandas as pd

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง - ซื้อขายตรง", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 12px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    .calc-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-top: 15px; }
    .mill-box-top { background-color: #FFF9C4; padding: 15px; border-radius: 8px; border: 1px solid #FFB300; border-left: 6px solid #FFB300; margin-bottom: 8px; }
    .mill-box-normal { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E0E0E0; border-left: 6px solid #B0BEC5; margin-bottom: 8px; }
    .role-box { background-color: #E8EAF6; padding: 10px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #3F51B5; }
    .stButton>button { width: 100%; font-size: 18px !important; height: 45px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ข้อมูลราคากลางฐานเริ่มต้นของแต่ละโรงสี (อ้างอิงความชื้นมาตรฐาน 15% ต้นข้าว 40 กรัม) ---
MILL_BASE_PRICES = {
    "1. โรงสีบ้านดี": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 18600.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8800.0,
        "ข้าวเหนียว กข6": 12100.0
    },
    "2. โรงสีนายบุญ": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 18450.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8700.0,
        "ข้าวเหนียว กข6": 11950.0
    },
    "3. โรงเจริญผล": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 18500.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8750.0,
        "ข้าวเหนียว กข6": 12000.0
    },
    "4. โรงสีธัญพืชผล": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 18550.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8900.0,
        "ข้าวเหนียว กข6": 12050.0
    },
    "5. โรงสีตากบ": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 18300.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8650.0,
        "ข้าวเหนียว กข6": 11800.0
    }
}

# --- ระบบจำลองฐานข้อมูลส่วนกลาง (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}
if 'rice_image' not in st.session_state:
    st.session_state.rice_image = None

# รายชื่อโรงสีทั้ง 5 แห่ง
MILL_NAMES = list(MILL_BASE_PRICES.keys())

# --- แถบเมนูด้านข้าง (Sidebar) ---
st.sidebar.image("https://flaticon.com", width=80)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")

# ส่วนจำลองสลับสถานะผู้ใช้งาน
st.sidebar.markdown('<div class="role-box"><b>🔄 จำลองสลับมุมมองผู้ใช้:</b></div>', unsafe_allow_html=True)
user_role = st.sidebar.radio("เลือกบทบาทผู้ใช้งานเพื่อทดสอบ", ["👨‍🌾 ฝั่งชาวนา", "🚛 ฝั่งรถขนข้าว (หน้างาน)"])

st.sidebar.write("---")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard/ระบบหลัก)", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🚛 ROLE: ฝั่งรถขนข้าว (หน้างาน)
# =========================================================================
if user_role == "🚛 ฝั่งรถขนข้าว (หน้างาน)":
    st.markdown('<p class="big-font">🚛 ระบบคนขับรถขนส่ง (ตรวจวัดคุณภาพหน้าแปลงนา)</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("💡 คำแนะนำการทดสอบ: ให้สลับไปที่บทบาท '👨‍🌾 ฝั่งชาวนา' เพื่อกดส่งข้อมูลแจ้งเรียกรถเข้ามาก่อนครับ")
    elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
        st.warning("📥 มีคำขอตรวจข้าวเข้ามาใหม่จากแปลงนา อ.โนนสูง")
        st.write(f"**📍 พื้นที่แปลงนา:** {st.session_state.order_detail['พื้นที่']}")
        st.write(f"**🌾 ชนิดข้าว:** {st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ ปริมาณประมาณการ:** {st.session_state.order_detail['ปริมาณ']} ตัน")
        
        if st.button("📍 ยืนยัน: เดินทางถึงหน้าแปลงนาชาวนาแล้ว"):
            st.session_state.order_status = "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน"
            st.rerun()
            
    elif st.session_state.order_status == "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน":
        st.subheader("📸 1. ถ่ายภาพสภาพกองข้าวเปลือกจริง")
        captured_photo = st.camera_input("ถ่ายรูปกองข้าวหน้างาน")
        if captured_photo is not None:
            st.session_state.rice_image = captured_photo
            st.success("📸 บันทึกรูปภาพเรียบร้อย!")
        
        st.write("---")
        st.subheader("🧪 2. บันทึกผลการวัดค่าคุณภาพจริง")
        actual_moisture = st.slider("💧 ค่าความชื้นจริงที่วัดได้ (%)", min_value=11, max_value=30, value=16)
        actual_pct = st.slider("🌾 เปอร์เซ็นต์ต้นข้าวสุ่มสีจริง (กรัม)", min_value=30, max_value=50, value=38)
        
        if st.button("📤 ส่งผลตรวจและรูปภาพเข้าระบบให้ชาวนาเลือกโรงสี"):
            if st.session_state.rice_image is None:
                st.error("⚠️ โปรดกดเปิดกล้องและถ่ายรูปกองข้าวก่อนส่งข้อมูลครับ")
            else:
                st.session_state.order_detail['ความชื้น'] = actual_moisture
                st.session_state.order_detail['เปอร์เซ็นต์ข้าว'] = actual_pct
                st.session_state.order_status = "รอชาวนาตัดสินใจเลือกโรงสี"
                st.success("ส่งข้อมูลผลตรวจเรียบร้อย! โปรดสลับบทบาทกลับไปที่ฝั่งชาวนาเพื่อเลือกโรงสี")
                st.rerun()
    else:
        st.success(f"สถานะปัจจุบัน: **{st.session_state.order_status}** (รถขนส่งกำลังรอการตัดสินใจจากชาวนา)")

# =========================================================================
# 👨‍🌾 ROLE: ฝั่งชาวนา
# =========================================================================
elif user_role == "👨‍🌾 ฝั่งชาวนา":
    if menu == "🏠 หน้าแรก (Dashboard/ระบบหลัก)":
        st.markdown('<p class="big-font">👨‍🌾 แอปพลิเคชันชาวนาโนนสูง (ระบบเลือกโรงสีตรง)</p>', unsafe_allow_html=True)
        
        if st.session_state.order_status == "ยังไม่มีรายการ":
            st.markdown('### 📊 รายการราคารับซื้อเกณฑ์มาตรฐานวันนี้ 5 โรงสี')
            view_rice_type = st.radio("กดเลือกดูราคาเกณฑ์แต่ละชนิดข้าว:", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            
            for mill, prices in MILL_BASE_PRICES.items():
                st.markdown(f"""
                <div style="background-color: #FAFAFA; padding: 10px; border-radius: 5px; border-left: 4px solid #1E5631; margin-bottom: 6px;">
                    <span style="float: right; color: #2E7D32; font-weight: bold;">{prices[view_rice_type]:,} บ./ตัน</span>
                    <b>{mill}</b>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
            st.markdown('<p class="big-font">🟢 ส่งข้อมูลเรียกรถตรวจคุณภาพข้าวหน้างาน</p>', unsafe_allow_html=True)
            
            calc_rice_type = st.selectbox("1. เลือกประเภทข้าวที่จะขาย", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            calc_amount = st.number_input("2. ปริมาณข้าวคาดการณ์ (ตัน)", min_value=0.1, max_value=100.0, value=5.0)
            sub_district = st.selectbox("3. เลือกตำบลที่นาของคุณ", ["โนนสูง", "ใหม่", "โตนด", "จันอัด", "ด่านคล้า", "ขามสะแกแสง", "พลสงคราม", "ลำคอหงษ์"])
            
            if st.button("🚛 ยืนยัน: เรียกรถคันกลางเข้าตรวจสอบหน้าแปลงนา"):
                st.session_state.order_status = "ชาวนาเรียกรถเข้าตรวจงาน"
                st.session_state.order_detail = {
                    "ประเภท": calc_rice_type,
                    "ปริมาณ": calc_amount,
                    "พื้นที่": f"ต.{sub_district} อ.โนนสูง โคราช"
                }
                st.success("เรียกรถสำเร็จ! โปรดสลับบทบาทผู้ใช้ที่เมนูด้านซ้ายเป็น '🚛 ฝั่งรถขนข้าว' เพื่อทดลองถ่ายภาพและตรวจข้าว")
                st.rerun()
                
        elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
            st.info("⏳ สถานะ: รถคันกลางได้รับพิกัดแล้ว กำลังเดินทางไปแปลงนาของคุณ...")
            
        elif st.session_state.order_status == "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน":
            st.warning("🧪 สถานะ: รถขนส่งมาถึงแล้ว! เจ้าหน้าที่กำลังถ่ายภาพและตรวจวัดคุณภาพจริง...")
            
        elif st.session_state.order_status == "รอชาวนาตัดสินใจเลือกโรงสี":
            st.markdown('<p class="big-font">👇 รายการคำนวณราคาสุทธิและกดเลือกโรงสีที่ต้องการ</p>', unsafe_allow_html=True)
            
            st.write(f"**🔬 ผลตรวจจากรถคันกลาง:** ข้าว{st.session_state.order_detail['ประเภท']} | ปริมาณ {st.session_state.order_detail['ปริมาณ']} ตัน")
            st.write(f"💧 ความชื้นจริง: {st.session_state.order_detail['ความชื้น']}% | 🌾 ต้นข้าวสุ่มสีได้: {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม")
            
            if st.session_state.rice_image is not None:
                st.image(st.session_state.rice_image, caption="ภาพกองข้าวของคุณจริงในระบบ", width=240)
            
            st.write("---")
            st.write("*ระบบคำนวณราคาหักลบจริงให้ของแต่ละโรงสีเรียบร้อยแล้ว เลือกโรงสีที่พอใจสูงสุดด้านล่างนี้ได้ทันที:*")
            
            # --- คำนวณราคาสุทธิของแต่ละโรงสีแบบ Dynamic ให้ชาวนาเห็นก่อนกดเลือก ---
            calculated_list = []
            rice_type = st.session_state.order_detail['ประเภท']
            moisture = st.session_state.order_detail['ความชื้น']
            rice_pct = st.session_state.order_detail['เปอร์เซ็นต์ข้าว']
            weight = st.session_state.order_detail['ปริมาณ']
            
            for mill_name, prices in MILL_BASE_PRICES.items():
                base_p = prices[rice_type]
                # สูตรหักความชื้น
                moist_diff = -(moisture - 15) * 150.0 if moisture > 15 else (15 - moisture) * 50.0
                # สูตรหักเปอร์เซ็นต์ข้าว
                pct_diff = (rice_pct - 40) * 200.0
                
                final_ton_price = base_p + moist_diff + pct_diff
                final_total_money = final_ton_price * weight
                
