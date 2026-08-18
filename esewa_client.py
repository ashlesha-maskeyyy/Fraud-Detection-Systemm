import streamlit as st
import requests
from datetime import datetime
import time

st.set_page_config(page_title="eSewa - Mobile Payment", page_icon="💸")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .header-style { 
        color: #60bb46; 
        font-size: 32px; 
        font-weight: bold; 
        text-align: center;
        margin-bottom: 20px;
    }
    div.stButton > button {
        background-color: #60bb46; 
        color: white; 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #4e9a38;
        color: white;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. App Header ---
st.markdown('<p class="header-style">eSewa</p>', unsafe_allow_html=True)
st.write(f"📅 {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')}")
st.divider()

st.subheader("Send Money")

with st.container():
    recipient = st.text_input("Recipient eSewa ID", placeholder="Mobile Number or Email")
    amount = st.number_input("Amount (NPR)", min_value=0.0, step=500.0)
    
    col1, col2 = st.columns(2)
    with col1:
        purpose = st.selectbox("Purpose", ["Personal Use", "Friend/Family", "Bill Payment", "Payment"])
    with col2:
        remarks = st.text_input("Remarks", value="Sent via eSewa")

    st.markdown("#### Security Verification")
    current_bal = st.number_input("Enter Your Current Balance", min_value=0.0)

if st.button("PROCEED"):
    if amount <= 0:
        st.warning("Please enter an amount greater than 0.")
    elif recipient == "":
        st.warning("Please enter a recipient ID.")
    elif current_bal < amount:
        st.error("Insufficient Balance.")
    else:
        with st.spinner('🔐 BuddhaAI is verifying your transaction...'):
            
            now = datetime.now()
            calculated_step = ((now.day - 1) * 24) + now.hour + 1
            
            expected_new_balance = current_bal - amount
            
            payload = {
                "step": calculated_step,
                "type": "TRANSFER", # 
                "amount": amount,
                "oldbalanceOrg": current_bal,
                "newbalanceOrig": expected_new_balance,
                "oldbalanceDest": 0.0, 
                "newbalanceDest": 0.0  
            }

            try:
                time.sleep(1.2)
                response = requests.post("http://127.0.0.1:8000/predict", json=payload)
                result = response.json()

                if result["verdict"] == "FRAUD":
                    st.markdown('<div style="background-color:#fee2e2; color:#b91c1c; padding:20px; border-radius:10px; border:1px solid #f87171;">', unsafe_allow_html=True)
                    st.error("### 🚫 TRANSACTION BLOCKED")
                    st.write(f"**Security Reason:** {result['reason']}")
                    st.write(f"**Risk Level:** {result['risk']}")
                    st.write("For your protection, this transfer has been halted. Please visit the nearest eSewa center for verification.")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.balloons()
                    st.success(f"Successfully sent NPR {amount:,.2f} to {recipient}")
                    st.write(f"**Transaction ID:** TXN{int(time.time())}")
                    st.write(f"**New Balance:** NPR {expected_new_balance:,.2f}")

            except Exception as e:
                st.error("Connection Failed: Ensure the FastAPI Backend (main.py) is running in the terminal.")