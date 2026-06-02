import streamlit as st
import pandas as pd

# ตั้งค่าหน้าตาแอปให้เหมาะสมกับมือถือ
st.set_page_config(page_title="แอปข้าวโนนสูง", page_icon="🌾", layout="centered")

# สไตล์ตกแต่งเพิ่มเติม
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1E5631; }
    .price-box { background-color: #F0F9F4; padding: 12px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 10px; }
    .calc-box { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-top: 15px; }
    .mill-box { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E0E0E0; margin-bottom: 8px; }
    .stButton>button { width: 100%; font-size: 20px !important; height: 50px; background-color: #2E7D32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ฐานข้อมูลราคารับซื้อของแต่ละโรงสี (ความชื้นมาตรฐาน 15%, เกณฑ์ต้นข้าว 40 กรัม) ---
# 💡 คุณสามารถปรับแก้ตัวเลขราคากลางตรงนี้ได้ตามต้องการเลยครับ
MILL_PRICES = {
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

# --- ระบบจำลองฐานข้อมูล (Session State) ---
if 'order_status' not in st.session_state:
    st.session_state.order_status = "ยังไม่มีรายการ"
if 'order_detail' not in st.session_state:
    st.session_state.order_detail = {}

# --- แถบเมนูด้านข้าง ---
st.sidebar.image("https://flaticon.com", width=100)
st.sidebar.title("🌾 ข้าวโนนสูง โคราช")
st.sidebar.write("ระบบเปรียบเทียบราคารับซื้อโรงสีท้องถิ่น")
menu = st.sidebar.radio("เลือกเมนูใช้งาน", ["🏠 หน้าแรก (Dashboard)", "📋 รายการของฉัน", "💬 กล่องข้อความ", "👤 ข้อมูลส่วนตัว"])

# =========================================================================
# 🏠 เมนู: หน้าแรก
# =========================================================================
if menu == "🏠 หน้าแรก (Dashboard)":
    st.markdown('<p class="big-font">📊 เครื่องคำนวณและเปรียบเทียบราคา 5 โรงสี</p>', unsafe_allow_html=True)
    st.write("ระบบจะคำนวณราคาหักลดความชื้นและคุณภาพข้าวให้สอดคล้องกับแต่ละโรงสีอัตโนมัติ")
    
    # ส่วนกรอกข้อมูลของชาวนา
    with st.container(border=True):
        st.subheader("🌾 ข้อมูลข้าวเปลือกของคุณ")
        calc_rice_type = st.selectbox("เลือกประเภทข้าว", ["ข้าวหอมมะลิ 105 (ปี 68/69)", "ข้าวเจ้าทั่วไป (นาปรังปี 69)", "ข้าวเหนียว กข6"])
        calc_amount = st.number_input("ใส่ปริมาณข้าวทั้งหมด (ตัน)", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            calc_moisture = st.slider("เปอร์เซ็นต์ความชื้น (%)", min_value=11, max_value=30, value=15)
        with col_input2:
            calc_rice_pct = st.slider("% ต้นข้าวจากการสุ่มสี (กรัม)", min_value=30, max_value=50, value=40)

    st.write("---")
    st.markdown('<p class="big-font">🏭 ตารางเปรียบเทียบราคาโรงสีใน อ.โนนสูง</p>', unsafe_allow_html=True)
    st.write("*คำนวณจากน้ำหนักและคุณภาพข้าวของคุณแล้ว โรงสีที่ให้ราคาสูงสุดจะอยู่บนสุด*")

    # --- ส่วนการคำนวณและประมวลผลราคาของแต่ละโรงสี ---
    calculated_mills = []
    
    for mill_name, prices in MILL_PRICES.items():
        base_price = prices[calc_rice_type]
        
        # 1. คำนวณหัก/เพิ่ม ความชื้น (เกิน 15% หักตันละ 150 บ., ต่ำกว่าเพิ่มตันละ 50 บ.)
        moisture_diff = 0.0
        if calc_moisture > 15:
            moisture_diff = -(calc_moisture - 15) * 150.0
        elif calc_moisture < 15:
            moisture_diff = (15 - calc_moisture) * 50.0
            
        # 2. คำนวณหัก/เพิ่ม เปอร์เซ็นต์ข้าว (ต่างจาก 40 กรัม คิดกรัมละ 200 บ.)
        rice_pct_diff = (calc_rice_pct - 40) * 200.0
        
        # ราคาต่อตันสุทธิและราคารวมของโรงสีนี้
        net_price_per_ton = base_price + moisture_diff + rice_pct_diff
        total_money = net_price_per_ton * calc_amount
        
        calculated_mills.append({
            "name": mill_name,
            "price_per_ton": net_price_per_ton,
            "total_money": total_money
        })
    
    # เรียงลำดับโรงสีที่ให้ราคารวมสูงสุดขึ้นก่อน (ชาวนาได้ประโยชน์ที่สุด)
    calculated_mills = sorted(calculated_mills, key=lambda x: x['total_money'], reverse=True)
    
    # แสดงผลรายการโรงสีแบบการ์ดเรียงลงมา
    for index, mill in enumerate(calculated_mills):
        # ไฮไลท์โรงสีที่ให้ราคาสูงที่สุดเป็นสีทอง/เขียวเด่น
        badge = "🏆 ให้ราคาสูงสุด" if index == 0 else ""
        
        st.markdown(f"""
        <div class="mill-box" style="background-color: {'#FFF9C4' if index == 0 else '#FFFFFF'}; border-left: 6px solid {'#FFB300' if index == 0 else '#B0BEC5'};">
            <span style="float: right; font-weight: bold; color: #E65100; font-size: 14px;">{badge}</span>
            <b style="font-size: 18px; color: #1E5631;">{mill['name']}</b><br>
            <span style="font-size: 14px; color: #555;">ราคาประเมินจริง: <b>{mill['price_per_ton']:,} บาท/ตัน</b></span><br>
            <span style="font-size: 20px; color: #D84315;">ยอดเงินรวมสุทธิที่คุณจะได้รับ: <b>{mill['total_money']:,} บาท</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        # เพิ่มปุ่มกดเลือกขายให้โรงสีนั้นๆ ข้างใต้การ์ด
        if st.button(f"🚀 ตกลงขายข้าวให้กับ {mill['name']}", key=f"btn_{mill['name']}"):
            st.session_state.order_status = "รอโรงสีตอบรับการนัดหมาย"
            st.session_state.order_detail = {
                "โรงสี": mill['name'],
                "ประเภท": calc_rice_type,
                "ปริมาณ": calc_amount,
                "ความชื้น": calc_moisture,
                "เปอร์เซ็นต์ข้าว": calc_rice_pct,
                "ราคาประเมิน": mill['total_money']
            }
            st.success(f"บันทึกรายการสำเร็จ! ระบบส่งข้อมูลใบเสนอราคาไปยัง {mill['name']} เรียบร้อยแล้ว")
            st.balloons()
            st.rerun()

# =========================================================================
# 📋 เมนู: รายการของฉัน
# =========================================================================
elif menu == "📋 รายการของฉัน":
    st.markdown('<p class="big-font">📋 สถานะการซื้อขายปัจจุบัน</p>', unsafe_allow_html=True)
    
    if st.session_state.order_status == "ยังไม่มีรายการ":
        st.info("คุณยังไม่มีรายการเสนอขายข้าวในขณะนี้ กลับไปที่หน้าแรกเพื่อคำนวณและเลือกโรงสี")
    else:
        st.write(f"**🏭 โรงสีที่เลือก:** {st.session_state.order_detail['โรงสี']}")
        st.write(f"**🌾 ชนิดข้าว:** {st.session_state.order_detail['ประเภท']}")
        st.write(f"**⚖️ น้ำหนักรวม:** {st.session_state.order_detail['ปริมาณ']} ตัน")
        st.write(f"**💧 คุณภาพข้าว:** ความชื้น {st.session_state.order_detail['ความชื้น']}% | ต้นข้าว {st.session_state.order_detail['เปอร์เซ็นต์ข้าว']} กรัม")
        st.markdown(f"### 💰 ยอดเงินที่จะได้รับ: <span style='color:#E65100;'>{st.session_state.order_detail['ราคาประเมิน']:,} บาท</span>", unsafe_allow_html=True)
        
        status = st.session_state.order_status
        st.warning(f"🔔 สถานะปัจจุบัน: **{status}**")
        
        if status == "รอโรงสีตอบรับการนัดหมาย":
            if st.button(f"จำลองสถานการณ์: {st.session_state.order_detail['โรงสี']} กดยืนยันคิวรถรับส่ง"):
                st.session_state.order_status = "รถขนส่งกำลังเดินทางไปแปลงนา"
                st.rerun()
        elif status == "รถขนส่งกำลังเดินทางไปแปลงนา":
            if st.button("จำลองสถานการณ์: รถชั่งน้ำหนักเรียบร้อย และตรวจสอบคุณภาพตรงกัน"):
                st.session_state.order_status = "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)"
                st.rerun()
        elif status == "ชำrateเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)" or status == "ชำระเงินสำเร็จ (เงินเข้าบัญชี ธ.ก.ส. แล้ว)":
            st.success("🎉 การซื้อขายเสร็จสิ้นสมบูรณ์! เงินถูกโอนเข้าบัญชีชาวนาเรียบร้อย")
            if st.button("เริ่มการขายล๊อตถัดไป"):
                st.session_state.order_status = "ยังไม่มีรายการ"
                st.rerun()

# =========================================================================
# เมนูอื่นๆ คงเดิมเพื่อความเสถียร
# =========================================================================
elif menu == "💬 กล่องข้อความ":
    st.markdown('<p class="big-font">💬 แชทติดต่อสอบถาม</p>', unsafe_allow_html=True)
    if st.session_state.order_status != "ยังไม่มีรายการ":
        st.write(f"ห้องสนทนาของท่านกับ: **{st.session_state.order_detail['โรงสี']}**")
    with st.container(border=True):
        st.write("**👨‍🌾 คุณ (ชาวนา):** สวัสดีครับ ปักหมุดที่นาโนนสูงให้แล้วนะครับ")
        st.write("**🏭 ฝ่ายรับซื้อของโรงสี:** ได้รับข้อมูลแล้วค่ะ เจ้าหน้าที่กำลังวางแผนจัดคิวรถพ่วงวิ่งเข้าจัดเก็บค่ะ")
    st.text_input("พิมพ์ข้อความติดต่อโรงสี...")
    st.button("ส่งข้อความ")

elif menu == "👤 ข้อมูลส่วนตัว":
    st.markdown('<p class="big-font">👤 ข้อมูลเกษตรกร</p>', unsafe_allow_html=True)
    st.text_input("ชื่อ - นามสกุล", value="นายสมศักดิ์ รักบ้านเกิด")
    st.text_input("เลขทะเบียนเกษตรกร (ทบก.)", value="1-3004-XXXXX-XX-X")
    st.subheader("🏦 บัญชีธนาคารสำหรับรับเงินค่าข้าว")
    st.text_input("ธนาคาร", value="ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (ธ.ก.ส.)")
    st.text_input("เลขที่บัญชี / PromptPay", value="020-1-XXXXX-X")
    st.button("บันทึกข้อมูลส่วนตัว")
