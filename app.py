import streamlit as st
import pandas as pd

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง - เลือกโรงสีตรง", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 12px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    .calc-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-top: 15px; }
    .mill-card-info { background-color: #FAFAFA; padding: 12px; border-radius: 8px; border: 1px solid #E0E0E0; border-left: 4px solid #1E5631; margin-bottom: 6px; }
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
# 👨‍🌾 ROLE: ฝั่งชาวนา
# =========================================================================
if user_role == "👨‍🌾 ฝั่งชาวนา":
    if menu == "🏠 หน้าแรก (Dashboard/ระบบหลัก)":
        st.markdown('<p class="big-font">👨‍🌾 แอปพลิเคชันชาวนาโนนสูง (ระบุโรงสีที่ต้องการขาย)</p>', unsafe_allow_html=True)
        
        if st.session_state.order_status == "ยังไม่มีรายการ":
            st.markdown('### 📊 1. เช็คราคารับซื้อเกณฑ์มาตรฐานวันนี้จาก 5 โรงสี')
            view_rice_type = st.radio("กดเลือกดูราคาเกณฑ์แต่ละชนิดข้าว:", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            
            for mill, prices in MILL_BASE_PRICES.items():
                st.markdown(f"""
                <div class="mill-card-info">
                    <span style="float: right; color: #2E7D32; font-weight: bold;">{prices[view_rice_type]:,} บ./ตัน</span>
                    <b>{mill}</b>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
            st.markdown('<p class="big-font">🎯 2. ติ๊กเลือกโรงสีและกรอกข้อมูลเพื่อส่งรถไปรับข้าว</p>', unsafe_allow_html=True)
            
            selected_mill_choice = st.radio("👇 โปรดติ๊กเลือกโรงสีที่คุณต้องการนำข้าวไปส่งขาย:", MILL_NAMES)
            calc_rice_type = st.selectbox("เลือกประเภทข้าวที่จะขาย", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            
            user_address = st.text_area("พิมพ์ที่อยู่แปลงนาอย่างละเอียด (ระบุบ้านเลขที่/หมู่บ้าน/ตำบล/จุดสังเกต/เบอร์โทร)", 
                                        placeholder="เช่น บ้านเลขที่ 99 หมู่ 3 บ้านด่านคล้า ตำบลโนนสูง อำเภอโนนสูง (ตรงข้ามสระน้ำกลางหมู่บ้าน)")
            
            st.caption("📍 กดเปิดสิทธิ์เข้าถึง GPS เพื่อปักหมุดตำแหน่งนาข้าว")
            st.checkbox("ยืนยันแชร์ตำแหน่งพิกัดแปลงนาปัจจุบันผ่านระบบ GPS ของมือถือ", value=True)
            
            if st.button("🚛 ยืนยัน: เลือกโรงสีนี้และเรียกรถรับข้าว"):
                if not user_address:
                    st.error("⚠️ โปรดระบุที่อยู่แปลงนาของคุณในช่องด้านบนก่อนกดปุ่มครับ")
                else:
                    st.session_state.order_status = "ชาวนาเรียกรถเข้าตรวจงาน"
                    st.session_state.order_detail = {
                        "ประเภท": calc_rice_type,
                        "ที่อยู่แปลงนา": user_address,
                        "เลือกโรงสี": selected_mill_choice
                    }
                    st.success(f"บันทึกข้อมูลเรียบร้อย! ส่งใบงานให้รถเตรียมวิ่งไปส่งข้าวที่ '{selected_mill_choice}' ตามที่คุณต้องการแล้ว")
                    st.rerun()
                
        elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
            st.info(f"⏳ สถานะ: รถคันกลางได้รับข้อมูลแล้ว กำลังเดินทางไปแปลงนาเพื่อบรรทุกข้าวไปส่งที่ **{st.session_state.order_detail['เลือกโรงสี']}** ตามที่คุณสั่ง")
            
        elif st.session_state.order_status == "กำลังตรวจวัดคุณภาพและน้ำหนัก":
            st.warning("🧪 สถานะ: รถขนส่งมาถึงแปลงนาแล้ว! กำลังโหลดข้าวขึ้นเครื่องชั่งและตรวจสอบเนื้อข้าว...")
            
        elif st.session_state.order_status == "รอชาวนายืนยันยอดเงินสุทธิ":
            st.markdown('<p class="big-font">💰 ตรวจสอบผลการชั่งน้ำหนักและยอดเงินสุทธิ</p>', unsafe_allow_html=True)
            st.write(f"**🏭 โรงสีที่คุณเลือกส่งไปขาย:** {st.session_state.order_detail['เลือกโรงสี']}")
            st.write(f"🌾 ชนิดข้าว: ข้าว{st.session_state.order_detail['ประเภท']}")
            st.write(f"⚖️ น้ำหนักสุทธิจากตราชั่ง: **{st.session_state.order_detail['ปริมาณ']} ตัน**")
            st.write(f"💧 ความชื้นจริง: {st.session_state.order_detail['ความชื้น']}% | 🌾 ต้นข้าวสุ่มสีได้: {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม")
            
            if st.session_state.rice_image is not None:
                st.image(st.session_state.rice_image, caption="ภาพถ่ายสภาพข้าวหน้างาน", width=240)
                
            st.write("---")
            st.markdown(f"""
            <div class="calc-box">
                <span style="font-size: 15px; color: #555;">💰 ยอดเงินรวมสุทธิที่คุณจะได้รับจาก {st.session_state.order_detail['เลือกโรงสี']}:</span><br>
                <span style="font-size: 32px; color: #D84315;"><b>{st.session_state.order_detail['raw_money']:,} บาท</b></span><br>
                <small>คิดเป็นเรตราคาเฉลี่ย: {st.session_state.order_detail['ราคาต่อตัน']:,} บาท/ตัน</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ ยืนยันยอดเงินสุทธิและอนุมัติการขาย"):
                st.session_state.order_status = "ตกลงขายและรอรับชำระเงิน"
                st.success("อนุมัติสำเร็จ! ระบบบันทึกข้อตกลงซื้อขายตรงกับโรงสีปลายทางแล้ว")
                st.rerun()
                
        elif st.session_state.order_status == "ตกลงขายและรอรับชำระเงิน":
            st.success(f"🤝 ซื้อขายตรงกับ **{st.session_state.order_detail['เลือกโรงสี']}** เรียบร้อย!")
            st.write(f"💰 ยอดเงินรวมสุทธิที่จะโอนเข้าบัญชี: **{st.session_state.order_detail['raw_money']:,} บาท**")
            st.write(f"📍 ที่อยู่จัดเก็บ: {st.session_state.order_detail['ที่อยู่แปลงนา']}")
            st.info("🚛 ข้าวเปลือกกำลังถูกเทส่งเข้าคลังโรงสี กรุณารอยอดเงินโอนจากโรงสีเข้าบัญชี ธ.ก.ส. ของคุณ...")
            
            if st.button("🔄 จำลอง: ได้รับเงินโอนเรียบร้อย (เริ่มล็อตใหม่)"):
                st.session_state.order_status = "ยังไม่มีรายการ"
                st.session_state.rice_image = None
                st.rerun()

# =========================================================================
# 🚛 ROLE: ฝั่งรถขนข้าว (หน้างาน)
# =========================================================================
elif user_role == "🚛 ฝั่งรถขนข้าว (หน้างาน)":
    st.markdown('<p class="big-font">🚛 ระบบคนขับรถขนส่ง (ใบงานวิ่งรับข้าวตามคำสั่งชาวนา)</p>', unsafe_allow_html=True)
    
    # 1. เคสที่ 1: ยังไม่มีรายการงานส่งเข้ามา
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("💡 คำแนะนำการทดสอบ: ให้สลับไปที่บทบาท '👨‍🌾 ฝั่งชาวนา' เพื่อเลือกโรงสีและปักหมุดแปลงนาก่อนครับ")
        
    # 2. เคสที่ 2: ชาวนากดเรียกรถมาแล้ว รอรถกดยืนยันว่าถึงหน้างาน
    elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
        st.warning("📥 มีใบสั่งงานขนข้าวเข้าสู่ระบบใหม่")
        st.markdown(f"🎯 **โรงสีเป้าหมายที่ชาวนาสั่ง:** <span style='font-size:18px; color:#2E7D32;'><b>{st.session_state.order_detail['เลือกโรงสี']}</b></span>", unsafe_allow_html=True)
        st.write(f"**📍 ที่อยู่แปลงนาชาวนา:** {st.session_state.order_detail['ที่อยู่แปลงนา']}")
        st.write(f"**🌾 ชนิดข้าว:** ข้าว{st.session_state.order_detail['ประเภท']}")
        
        st.caption("📌 แผนที่นำทาง GPS วิ่งไปนาข้าวชาวนา (จำลอง)")
        st.map(pd.DataFrame({'lat': [15.1814], 'lon': [102.2531]}))
        
        if st.button("📍 ยืนยัน: เดินทางถึงแปลงนาและนำข้าวพ่วงไปขึ้นตราชั่งแล้ว"):
            st.session_state.order_status = "กำลังตรวจวัดคุณภาพและน้ำหนัก"
            st.rerun()
            
