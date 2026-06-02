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
    .mill-card-selected { background-color: #FFF9C4; padding: 15px; border-radius: 8px; border: 2px solid #FFB300; border-left: 6px solid #FFB300; margin-bottom: 10px; }
    .mill-card-normal { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E0E0E0; border-left: 6px solid #B0BEC5; margin-bottom: 10px; }
    .role-box { background-color: #E8EAF6; padding: 10px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #3F51B5; }
    .stButton>button { width: 100%; font-size: 18px !important; height: 45px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ข้อมูลราคากลางฐานเริ่มต้นของแต่ละโรงสี (อ้างอิงความชื้นมาตรฐาน 15% ต้นข้าว 40 กรัม) ---
MILL_BASE_PRICES = {
    "1. โรงสีบ้านดี": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 15600.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8800.0,
        "ข้าวเหนียว กข6": 12100.0
    },
    "2. โรงสีนายบุญ": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 15450.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8700.0,
        "ข้าวเหนียว กข6": 11950.0
    },
    "3. โรงเจริญผล": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 15500.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8750.0,
        "ข้าวเหนียว กข6": 12000.0
    },
    "4. โรงสีธัญพืชผล": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 15550.0,
        "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8900.0,
        "ข้าวเหนียว กข6": 12050.0
    },
    "5. โรงสีตากบ": {
        "ข้าวหอมมะลิ 105 (ปี 68/69)": 15300.0,
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
    st.markdown('<p class="big-font">🚛 ระบบคนขับรถขนส่ง (ตรวจวัดคุณภาพและชั่งน้ำหนักจริง)</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("💡 คำแนะนำการทดสอบ: ให้สลับไปที่บทบาท '👨‍🌾 ฝั่งชาวนา' เพื่อพิมพ์ที่อยู่ปักหมุดเรียกรถเข้ามาก่อนครับ")
    elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
        st.warning("📥 มีคำขอเก็บเกี่ยว/ขนส่งข้าวเข้ามาใหม่")
        st.write(f"**📍 ที่อยู่จัดส่งหน้างาน:** {st.session_state.order_detail['ที่อยู่แปลงนา']}")
        st.write(f"**🌾 ชนิดข้าว:** ข้าว{st.session_state.order_detail['ประเภท']}")
        
        # แสดงแผนที่จำลองพิกัดปักหมุดที่ชาวนาส่งมา
        st.caption("📌 แผนที่พิกัดนาข้าวของชาวนา (จำลอง)")
        st.map(pd.DataFrame({'lat': [15.1814], 'lon': [102.2531]}))
        
        if st.button("📍 ยืนยัน: เดินทางถึงแปลงนาและนำข้าวไปขึ้นตราชั่งแล้ว"):
            st.session_state.order_status = "กำลังตรวจวัดคุณภาพและน้ำหนัก"
            st.rerun()
            
    elif st.session_state.order_status == "กำลังตรวจวัดคุณภาพและน้ำหนัก":
        st.subheader("📸 1. ถ่ายภาพสภาพกองข้าวเปลือกจริง")
        captured_photo = st.camera_input("ถ่ายรูปกองข้าวหน้างาน")
        if captured_photo is not None:
            st.session_state.rice_image = captured_photo
            st.success("📸 บันทึกรูปภาพเรียบร้อย!")
        
        st.write("---")
        st.subheader("🧪 2. บันทึกผลการวัดค่าคุณภาพและน้ำหนักจากแท่นชั่งจริง")
        
        # ย้ายช่องกรอกน้ำหนักรวมสุทธิมาให้คนขับรถกรอกตรงนี้ตามโจทย์
        actual_weight = st.number_input("⚖️ น้ำหนักข้าวสุทธิจริงที่ชั่งได้ (ตัน)", min_value=0.1, max_value=120.0, value=12.5, step=0.1)
        actual_moisture = st.slider("💧 ค่าความชื้นจริงที่วัดได้ (%)", min_value=11, max_value=30, value=16)
        actual_pct = st.slider("🌾 เปอร์เซ็นต์ต้นข้าวสุ่มสีจริง (กรัม)", min_value=30, max_value=50, value=38)
        
        if st.button("📤 ส่งผลตรวจและน้ำหนักจริงเข้าระบบเพื่อให้ชาวนาเลือกโรงสี"):
            if st.session_state.rice_image is None:
                st.error("⚠️ โปรดกดเปิดกล้องและถ่ายรูปกองข้าวก่อนส่งข้อมูลครับ")
            else:
                st.session_state.order_detail['ปริมาณ'] = actual_weight
                st.session_state.order_detail['ความชื้น'] = actual_moisture
                st.session_state.order_detail['เปอร์เซ็นต์ข้าว'] = actual_pct
                st.session_state.order_status = "รอชาวนาตัดสินใจเลือกโรงสี"
                st.success("ส่งข้อมูลผลตรวจเรียบร้อย! โปรดสลับบทบาทกลับไปที่ฝั่งชาวนาเพื่อเลือกโรงสี")
                st.rerun()
    else:
        st.success(f"สถานะปัจจุบัน: **{st.session_state.order_status}** (รถขนส่งบันทึกข้อมูลเรียบร้อยแล้ว)")

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
            st.markdown('<p class="big-font">🟢 กรอกข้อมูลแปลงนาเพื่อเรียกรถเข้าตรวจสอบ</p>', unsafe_allow_html=True)
            
            calc_rice_type = st.selectbox("1. เลือกประเภทข้าวที่จะเสนอขาย", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            
            # เปลี่ยนระบบตำบลเป็นพิมพ์ที่อยู่จัดส่งละเอียดตามโจทย์
            user_address = st.text_area("2. พิมพ์ที่อยู่แปลงนาอย่างละเอียด (ระบุบ้านเลขที่/หมู่บ้าน/ตำบล/จุดสังเกต)", 
                                        placeholder="เช่น บ้านเลขที่ 99 หมู่ 3 บ้านด่านคล้า ตำบลโนนสูง อำเภอโนนสูง (ตรงข้ามสระน้ำกลางหมู่บ้าน)")
            
            st.caption("📍 3. กดเปิดสิทธิ์เข้าถึง GPS เพื่อปักหมุดตำแหน่งนาข้าวของคุณลงในระบบ")
            st.checkbox("📍 ยืนยันแชร์ตำแหน่งพิกัดแปลงนาปัจจุบันผ่านระบบ GPS ของมือถือ", value=True)
            
            if st.button("🚛 ยืนยัน: ส่งที่อยู่และปักหมุดเรียกรถคันกลาง"):
                if not user_address:
                    st.error("⚠️ โปรดระบุที่อยู่แปลงนาของคุณในช่องด้านบนก่อนกดเรียกรถครับ")
                else:
                    st.session_state.order_status = "ชาวนาเรียกรถเข้าตรวจงาน"
                    st.session_state.order_detail = {
                        "ประเภท": calc_rice_type,
                        "ที่อยู่แปลงนา": user_address
                    }
                    st.success("เรียกรถสำเร็จ! โปรดสลับบทบาทผู้ใช้ด้านซ้ายเป็น '🚛 ฝั่งรถขนข้าว' เพื่อจำลองการถ่ายภาพ วัดความชื้นและชั่งน้ำหนักจริง")
                    st.rerun()
                
        elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
            st.info("⏳ สถานะ: รถคันกลางได้รับพิกัดที่อยู่ของคุณแล้ว กำลังเดินทางไปแปลงนา...")
            
        elif st.session_state.order_status == "กำลังตรวจวัดคุณภาพและน้ำหนัก":
            st.warning("🧪 สถานะ: รถขนส่งมาถึงแล้ว! เจ้าหน้าที่กำลังถ่ายภาพ ตรวจคุณภาพ และวัดน้ำหนักจริงจากแท่นชั่ง...")
            
        elif st.session_state.order_status == "รอชาวนาตัดสินใจเลือกโรงสี":
            st.markdown('<p class="big-font">👇 ติ๊กเลือกโรงสีที่คุณต้องการขายข้าวให้</p>', unsafe_allow_html=True)
            
            st.write(f"**🔬 รายงานผลตรวจจริง:** ข้าว{st.session_state.order_detail['ประเภท']}")
            st.write(f"⚖️ น้ำหนักสุทธิจากตราชั่ง: **{st.session_state.order_detail['ปริมาณ']} ตัน**")
            st.write(f"💧 ความชื้นจริง: {st.session_state.order_detail['ความชื้น']}% | 🌾 ต้นข้าวสุ่มสีได้: {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม")
            
            if st.session_state.rice_image is not None:
                st.image(st.session_state.rice_image, caption="ภาพถ่ายสภาพข้าวของคุณจริงในระบบ", width=240)
            
            st.write("---")
