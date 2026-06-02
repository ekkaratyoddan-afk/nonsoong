import streamlit as st
import pandas as pd

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง - ระบบประมูล", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 12px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    .calc-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-top: 15px; }
    .mill-box { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E0E0E0; margin-bottom: 8px; }
    .role-box { background-color: #E8EAF6; padding: 10px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #3F51B5; }
    .stButton>button { width: 100%; font-size: 18px !important; height: 45px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบจำลองฐานข้อมูลส่วนกลาง (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}
if 'mill_bids' not in st.session_state:
    st.session_state.mill_bids = {}

# รายชื่อโรงสีทั้ง 5 แห่ง
MILL_NAMES = ["1. โรงสีบ้านดี", "2. โรงสีนายบุญ", "3. โรงเจริญผล", "4. โรงสีธัญพืชผล", "5. โรงสีตากบ"]

# --- แถบเมนูด้านข้าง (Sidebar) ---
st.sidebar.image("https://flaticon.com", width=80)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")

# 🔘 ส่วนสำคัญ: ตัวจำลองสลับสถานะผู้ใช้งาน เพื่อให้ทดสอบระบบได้ในแอปเดียว
st.sidebar.markdown('<div class="role-box"><b>🔄 จำลองสลับมุมมองผู้ใช้:</b></div>', unsafe_allow_html=True)
user_role = st.sidebar.radio("เลือกบทบาทผู้ใช้งานเพื่อทดสอบ", ["👨‍🌾 ฝั่งชาวนา", "🚛 ฝั่งรถขนข้าว (หน้างาน)", "🏭 ฝั่งโรงสี (เปิดประมูล)"])

st.sidebar.write("---")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard/ระบบหลัก)", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🚛 ROLE: ฝั่งรถขนข้าว (หน้างาน)
# =========================================================================
if user_role == "🚛 ฝั่งรถขนข้าว (หน้างาน)":
    st.markdown('<p class="big-font">🚛 ระบบคนขับรถขนส่ง (ตรวจวัดคุณภาพหน้าแปลงนา)</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("💡 คำแนะนำการทดสอบ: ให้สลับไปที่บทบาท '👨‍🌾 ฝั่งชาวนา' เพื่อกดแจ้งเรียกรถและปักหมุดแปลงนาก่อนครับ")
    elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
        st.warning("📥 มีคำขอตรวจข้าวเข้ามาใหม่จากแปลงนา อ.โนนสูง")
        st.write(f"**📍 พื้นที่:** {st.session_state.order_detail['พื้นที่']}")
        st.write(f"**🌾 พันธุ์ข้าวที่ชาวนาแจ้งเบื้องต้น:** {st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ ปริมาณคาดการณ์:** {st.session_state.order_detail['ปริมาณ']} ตัน")
        
        if st.button("📍 ยืนยัน: เดินทางถึงหน้าแปลงนาแล้ว (กำลังตรวจสอบล็อกข้าว)"):
            st.session_state.order_status = "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน"
            st.rerun()
            
    elif st.session_state.order_status == "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน":
        st.subheader("🧪 บันทึกผลการสุ่มตรวจคุณภาพจริงหน้างาน")
        st.write("ให้นำข้าวเปลือกเข้าเครื่องวัดความชื้นและเครื่องกะเทาะทดลองสี แล้วกรอกค่าจริงลงระบบ:")
        
        actual_moisture = st.slider("💧 ค่าความชื้นจริงที่วัดได้หน้างาน (%)", min_value=11, max_value=30, value=16)
        actual_pct = st.slider("🌾 เปอร์เซ็นต์ต้นข้าวสุ่มสีจริง (กรัม)", min_value=30, max_value=50, value=38)
        
        if st.button("📤 ส่งผลตรวจคุณภาพให้ 5 โรงสีเพื่อเปิดประมูลราคา"):
            st.session_state.order_detail['ความชื้น'] = actual_moisture
            st.session_state.order_detail['เปอร์เซ็นต์ข้าว'] = actual_pct
            st.session_state.order_status = "เปิดระบบประมูลราคากลาง"
            
            # รีเซ็ตราคาราคาประมูลเริ่มต้นให้แต่ละโรงสีคำนวณราคาฐานของตัวเองอัตโนมัติ
            for mill in MILL_NAMES:
                st.session_state.mill_bids[mill] = 0.0 
                
            st.success("ส่งข้อมูลผลตรวจเรียบร้อย! ตอนนี้ระบบส่งข้อมูลแจ้งเตือนไปยังโรงสีทั้ง 5 แห่งแล้ว")
            st.rerun()
            
    else:
        st.success(f"สถานะปัจจุบันของรายการนี้คือ: **{st.session_state.order_status}** (รถขนส่งกำลังรอขั้นตอนต่อไป)")

# =========================================================================
# 🏭 ROLE: ฝั่งโรงสี (เปิดประมูล)
# =========================================================================
elif user_role == "🏭 ฝั่งโรงสี (เปิดประมูล)":
    st.markdown('<p class="big-font">🏭 ระบบบริหารฝั่งโรงสีข้าว (อ.โนนสูง)</p>', unsafe_allow_html=True)
    
    selected_mill = st.selectbox("🏬 ทดลองสวมบทบาทเป็นโรงสีไหนในระบบ:", MILL_NAMES)
    
    if st.session_state.order_status != "เปิดระบบประมูลราคากลาง":
        st.info("⏳ กำลังรอข้อมูลคุณภาพข้าวผลตรวจจากรถขนส่งหน้าแปลงนา...")
    else:
        st.markdown("""<style>.mill-card { background-color: #E0F2F1; padding: 15px; border-radius: 10px; margin-bottom: 15px; }</style>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="mill-card">
            <h4>📢 ประกาศประมูลข้าวเปลือกด่วน!</h4>
            <b>📍 พิกัดนาข้าว:</b> {st.session_state.order_detail['พื้นที่']}<br>
            <b>🌾 ชนิดข้าว:</b> {st.session_state.order_detail['ประเภท']} | <b>⚖️ ปริมาณ:</b> {st.session_state.order_detail['ปริมาณ']} ตัน<br>
            <span style="color:#D84315;"><b>🔬 ผลตรวจจากคนขับรถ (กลาง): ความชื้น {st.session_state.order_detail['ความชื้น']}% | ต้นข้าว {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        # ช่องกรอกราคาแข่งกันประมูล (กรอกราคาต่อตัน)
        current_bid = st.session_state.mill_bids.get(selected_mill, 0.0)
        st.write(f"ราคาที่คุณเก็งไว้ปัจจุบัน: **{current_bid:,.2f} บาท/ตัน**")
        
        bid_input = st.number_input("💵 เสนอราคารับซื้อของคุณ (บาทต่อตัน)", min_value=5000, max_value=25000, value=12000, step=50)
        
        if st.button(f"🎯 ส่งราคาเสนอซื้อจาก {selected_mill}"):
            st.session_state.mill_bids[selected_mill] = float(bid_input)
            st.success(f"ส่งราคาประมูลของ {selected_mill} เข้าระบบเรียบร้อยแล้ว! (ชาวนาจะเห็นราคานี้อัปเดตทันที)")

# =========================================================================
# 👨‍🌾 ROLE: ฝั่งชาวนา
# =========================================================================
elif user_role == "👨‍🌾 ฝั่งชาวนา":
    if menu == "🏠 หน้าแรก (Dashboard/ระบบหลัก)":
        st.markdown('<p class="big-font">👨‍🌾 แอปพลิเคชันชาวนาโนนสูง (ระบบเรียกประมูลราคา)</p>', unsafe_allow_html=True)
        
        if st.session_state.order_status == "ยังไม่มีรายการ":
            st.markdown('<div class="price-box"><b>💡 ขั้นตอนการใช้งาน:</b><br>กรอกข้อมูลที่นาด้านล่างเพื่อเรียกรถขนข้าวเคลื่อนที่เข้าไปสุ่มตรวจเปอร์เซ็นต์ความชื้นและเนื้อข้าวถึงหน้างานฟรี</div>', unsafe_allow_html=True)
            
            calc_rice_type = st.selectbox("1. เลือกประเภทข้าวที่จะขาย", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
            calc_amount = st.number_input("2. ปริมาณข้าวคาดการณ์โดยประมาณ (ตัน)", min_value=0.1, max_value=100.0, value=5.0)
            sub_district = st.selectbox("3. เลือกตำบลที่นาของคุณ", ["โนนสูง", "ใหม่", "โตนด", "จันอัด", "ด่านคล้า", "ขามสะแกแสง", "พลสงคราม", "ลำคอหงษ์"])
            
            if st.button("🚛 เรียกรถขนส่งเข้าตรวจสอบหน้าแปลงนา"):
                st.session_state.order_status = "ชาวนาเรียกรถเข้าตรวจงาน"
                st.session_state.order_detail = {
                    "ประเภท": calc_rice_type,
                    "ปริมาณ": calc_amount,
                    "พื้นที่": f"ต.{sub_district} อ.โนนสูง โคราช"
                }
                st.success("เรียกรถสำเร็จ! โปรดสลับบทบาทผู้ใช้ที่เมนูด้านซ้ายเป็น '🚛 ฝั่งรถขนข้าว' เพื่อทดลองตรวจข้าว")
                st.rerun()
                
        elif st.session_state.order_status == "ชาวนาเรียกรถเข้าตรวจงาน":
            st.info("⏳ สถานะ: รถขนข้าวคันกลางได้รับพิกัดแล้ว กำลังเดินทางมาที่หน้าแปลงนาของคุณ...")
            
        elif st.session_state.order_status == "กำลังตรวจวัดเปอร์เซ็นต์หน้างาน":
            st.warning("🧪 สถานะ: รถขนส่งมาถึงแล้ว! เจ้าหน้าที่กำลังสุ่มวัดเปอร์เซ็นต์ข้าวและความชื้นหน้าแปลงนา...")
            
        elif st.session_state.order_status == "เปิดระบบประมูลราคากลาง":
            st.markdown('<p class="big-font">🏆 ผลการตรวจคุณภาพและการเสนอราคาจาก 5 โรงสี</p>', unsafe_allow_html=True)
            
            # สรุปผลจากคนตรวจให้ชาวนาเห็น
            st.markdown(f"""
            <div class="calc-box" style="background-color: #E8F5E9; border-left: 5px solid #4CAF50;">
                <b>🔬 ผลตรวจรับรองคุณภาพกลาง (จากรถขนส่ง):</b><br>
                🌾 ชนิดข้าว: ข้าว{st.session_state.order_detail['ประเภท']}<br>
                💧 เปอร์เซ็นต์ความชื้นจริง: {st.session_state.order_detail['ความชื้น']}%<br>
                🌾 เปอร์เซ็นต์ต้นข้าวที่สีได้: {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม
            </div>
            """, unsafe_allow_html=True)
            
            st.write("*(💡 คำแนะนำทดสอบ: สลับเป็นบทบาท '🏭 ฝั่งโรงสี' ด้านซ้ายเพื่อพิมพ์ราคาประมูลแข่งกันก่อนได้ครับ)*")
            
            # ดึงราคาที่โรงสีกดประมูลมาแสดงเปรียบเทียบ
            bidding_results = []
            for mill, price_per_ton in st.session_state.mill_bids.items():
                if price_per_ton > 0: # โรงสีที่เข้ามากดประมูลแล้ว
                    total_money = price_per_ton * st.session_state.order_detail['ปริมาณ']
                    bidding_results.append({"name": mill, "per_ton": price_per_ton, "total": total_money})
                    
            if not bidding_results:
