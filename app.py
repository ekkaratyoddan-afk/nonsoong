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

# --- ข้อมูลราคากลางฐาน 2569 (ความชื้นมาตรฐาน 15%, เกณฑ์ต้นข้าวมาตรฐาน 40 กรัม) ---
BASE_PRICES = {
    "ข้าวหอมมะลิ 105 (ปี 68/69)": 15500.0,
    "ข้าวเจ้าทั่วไป (นาปรังปี 69)": 8750.0,
    "ข้าวเหนียว กข6": 12000.0
}

# --- ระบบจำลองฐานข้อมูล (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}

# --- แถบเมนูด้านข้าง ---
st.sidebar.image("https://flaticon.com", width=100)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")
st.sidebar.write("ระบบรับซื้อ-ขายข้าวและบริการเกษตร")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard)", "📋 รายการของฉัน", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🏠 เมนู: หน้าแรก
# =========================================================================
if menu == "🏠 หน้าแรก (Dashboard)":
    st.markdown('<p class="big-font">🌾 ราคารับซื้อเกณฑ์มาตรฐาน อ.โนนสูง</p>', unsafe_allow_html=True)
    st.write("*ราคาประเมินอ้างอิงความชื้น 15% และต้นข้าวระดับมาตรฐาน*")
    
    # แสดงราคากลางรายตัว
    cols = st.columns(3)
    for i, (rice_name, r_price) in enumerate(BASE_PRICES.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="price-box" style="font-size: 13px;">
                <b>{rice_name}</b><br>
                <span style="font-size: 18px; color: #2E7D32;"><b>{r_price:,}</b></span> บ./ตัน
            </div>
            """, unsafe_allow_html=True)
        
    st.write("---")
    
    # 🧮 เครื่องคำนวณราคากลางขั้นสูง (ความชื้น + เปอร์เซ็นต์ข้าว)
    st.markdown('<p class="big-font">🧮 เครื่องคำนวณราคา (ความชื้น + % ต้นข้าว)</p>', unsafe_allow_html=True)
    
    calc_rice_type = st.selectbox("1. เลือกประเภทข้าวของคุณ", list(BASE_PRICES.keys()), key="calc_type")
    calc_amount = st.number_input("2. ใส่ปริมาณข้าวทั้งหมด (ตัน)", min_value=0.1, max_value=100.0, value=1.0, step=0.5, key="calc_weight")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        calc_moisture = st.slider("3. เปอร์เซ็นต์ความชื้น (%)", min_value=11, max_value=30, value=15, key="calc_moist")
    with col_input2:
        calc_rice_pct = st.slider("4. % ต้นข้าวจากการสุ่มสี (กรัม)", min_value=30, max_value=50, value=40, key="calc_pct")
    
    # --- สูตรคำนวณทางคณิตศาสตร์สไตล์โรงสี ---
    base_price_per_ton = BASE_PRICES[calc_rice_type]
    
    # 1. คำนวณหัก/เพิ่ม จากความชื้น (เกณฑ์มาตรฐาน 15%)
    moisture_diff_money = 0.0
    if calc_moisture > 15:
        # ความชื้นเกิน หักตันละ 150 บาทต่อเปอร์เซ็นต์ที่เกิน
        moisture_diff_money = -(calc_moisture - 15) * 150.0
    elif calc_moisture < 15:
        # ข้าวแห้งดี ได้เพิ่มตันละ 50 บาทต่อเปอร์เซ็นต์ที่ลดลง
        moisture_diff_money = (15 - calc_moisture) * 50.0
        
    # 2. คำนวณหัก/เพิ่ม จากเปอร์เซ็นต์ต้นข้าว (เกณฑ์มาตรฐานอยู่ที่ 40 กรัม)
    # โรงสีจะให้ราคาเพิ่มหรือลดประมาณ ตันละ 200 บาท ต่อ 1 กรัมต้นข้าวที่เปลี่ยนแปลง
    rice_pct_diff_money = (calc_rice_pct - 40) * 200.0
    
    # สรุปราคาต่อตันสุทธิ
    final_price_per_ton = base_price_per_ton + moisture_diff_money + rice_pct_diff_money
    
    # คำนวณราคารวมทั้งหมด
    total_money = final_price_per_ton * calc_amount
    
    # คำอธิบายประกอบเหตุผล
    note_details = []
    if calc_moisture > 15: note_details.append(f"หักความชื้นเกิน (-{abs(moisture_diff_money):,} บ.)")
    elif calc_moisture < 15: note_details.append(f"เพิ่มค่าข้าวแห้ง (+{moisture_diff_money:,} บ.)")
    
    if calc_rice_pct > 40: note_details.append(f"โบนัสข้าวเต็มเมล็ดสวย (+{rice_pct_diff_money:,} บ.)")
    elif calc_rice_pct < 40: note_details.append(f"หักข้าวหักเยอะเกินเกณฑ์ (-{abs(rice_pct_diff_money):,} บ.)")
    
    note_text = " / ".join(note_details) if note_details else "คุณภาพตรงตามเกณฑ์มาตรฐานเป๊ะ"
    
    # แสดงผลลัพธ์แบบเด่นชัด
    st.markdown(f"""
    <div class="calc-box">
        <span style="font-size: 15px; color: #555;">💰 เงินสุทธิคาดการณ์ที่ชาวนาจะได้รับ:</span><br>
        <span style="font-size: 34px; color: #E65100;"><b>{total_money:,} บาท</b></span><br>
        <small><b>ราคาประเมินจริง:</b> ตันละ {final_price_per_ton:,} บาท</small><br>
        <small style="color: #757575;"><b>หมายเหตุระบบ:</b> {note_text}</small>
    </div>
    """, unsafe_allow_html=True)
        
    st.write("---")
    
    # ปุ่มส่งข้อมูลขายข้าวไปยังโรงสี
    st.markdown('<p class="big-font">🟢 ส่งข้อมูลเสนอขายข้าว</p>', unsafe_allow_html=True)
    
    with st.expander("คลิกที่นี่เพื่อส่งข้อมูลข้าวล๊อตนี้ให้โรงสีในอำเภอโนนสูงประมูลราคา"):
        sub_district = st.selectbox("เลือกตำบลของคุณ", ["โนนสูง", "ใหม่", "โตนด", "จันอัด", "ด่านคล้า", "ขามสะแกแสง", "พลสงคราม", "ลำคอหงษ์"])
        gps_mock = st.text_input("พิกัดแปลงนาของคุณ", "15.1814° N, 102.2531° E (อ.โนนสูง โคราช)")
        
        if st.button("🚀 ยืนยันการส่งข้อมูลขายข้าว"):
            st.session_state.order_status = "โรงสีกำลังเสนอราคา"
            st.session_state.order_detail = {
                "ประเภท": calc_rice_type,
                "ปริมาณ": calc_amount,
                "ความชื้น": calc_moisture,
                "เปอร์เซ็นต์ข้าว": calc_rice_pct,
                "ราคาประเมิน": total_money,
                "พื้นที่": f"ต.{sub_district} อ.โนนสูง"
            }
            st.success("ส่งข้อมูลสำเร็จ! ระบบกำลังส่งข้อมูลให้โรงสีพาร์ทเนอร์ในพื้นที่โคราชติดต่อกลับ")
            st.balloons()

# =========================================================================
# 📋 เมนู: รายการของฉัน
# =========================================================================
elif menu == "📋 รายการของฉัน":
    st.markdown('<p class="big-font">📋 สถานะการขายข้าวปัจจุบัน</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("คุณยังไม่มีรายการขายข้าวในขณะนี้ กลับไปที่หน้าแรกเพื่อส่งข้อมูล")
    else:
        st.write(f"**🌾 ชนิดข้าว:** {st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ น้ำหนักรวม:** {st.session_state.order_detail['ปริมาณ']} ตัน")
        st.write(f"**💧 ความชื้น:** {st.session_state.order_detail['ความชื้น']}% | **🌾 ต้นข้าว:** {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม")
        st.write(f"**💰 ยอดเงินในระบบ:** {st.session_state.order_detail['ราคาประเมิน']:,} บาท")
        st.write(f"**📍 พื้นที่นัดหมาย:** {st.session_state.order_detail['พื้นที่']}")
        
        status = st.session_state.order_status
        st.warning(f"🔔 สถานะปัจจุบัน: **{status}**")
        
        if status == "โรงสีกำลังเสนอราคา":
            if st.button("ตกลงขายราคานี้ให้กับ โรงสีโนนสูงเจริญการค้า"):
                st.session_state.order_status = "รถขนส่งกำลังเดินทางไปแปลงนา"
                st.rerun()
        elif status == "รถขนส่งกำลังเดินทางไปแปลงนา":
            if st.button("จำลองสถานการณ์: รถชั่งน้ำหนักเสร็จสิ้น และชาวนากดรับเงิน"):
                st.session_state.order_status = "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)"
                st.rerun()
        elif status == "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)":
            st.success("🎉 การซื้อขายเสร็จสิ้น! ระบบโอนเงินผ่านระบบ Fast Payment เรียบร้อย")
            if st.button("เริ่มการขายล๊อตถัดไป"):
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
