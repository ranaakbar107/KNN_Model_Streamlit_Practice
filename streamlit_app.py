import streamlit as st
import requests

# 1. Page setup
st.set_page_config(page_title="Diabetes Risk Predictor", layout="centered")
st.title("Diabetes Risk Predictor")
st.write("Enter the patient's medical details below to check the diabetes risk.")

# streamlit_app.py mein API_URL wali line ki jagah ye likhein:
st.sidebar.header("API Configuration")
API_URL = st.sidebar.text_input("FastAPI URL (Local or ngrok):", value="http://127.0.0.1:8000").rstrip("/")

# 2. Eight input widgets laid out in two columns
col1, col2 = st.columns(2)

with col1:
    pregnancies = st.number_input("Pregnancies", min_value=0, max_value=17, value=2, step=1)
    glucose = st.slider("Glucose", min_value=0.0, max_value=200.0, value=120.0, step=1.0)
    blood_pressure = st.slider("Blood Pressure", min_value=0.0, max_value=130.0, value=70.0, step=1.0)
    skin_thickness = st.slider("Skin Thickness", min_value=0.0, max_value=100.0, value=20.0, step=1.0)

with col2:
    insulin = st.slider("Insulin", min_value=0.0, max_value=850.0, value=80.0, step=1.0)
    bmi = st.slider("BMI", min_value=0.0, max_value=70.0, value=25.0, step=0.1)
    dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5, step=0.01)
    age = st.slider("Age", min_value=18, max_value=90, value=30, step=1)

st.divider()

# 3. Predict button and API call
if st.button("Predict", use_container_width=True):
    # Exact field names from PatientFeatures model in main.py
    payload = {
        "Pregnancies": int(pregnancies),
        "Glucose": float(glucose),
        "BloodPressure": float(blood_pressure),
        "SkinThickness": float(skin_thickness),
        "Insulin": float(insulin),
        "BMI": float(bmi),
        "DiabetesPedigreeFunction": float(dpf),
        "Age": int(age)
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            result_label = data["result_label"]
            confidence = data["confidence"]

            # 4. Clear result display
            if result_label == "Diabetic":
                st.error(f"Prediction: **{result_label}**")
            else:
                st.success(f"Prediction: **{result_label}**")

            # Show confidence as a percentage with st.metric
            st.metric(label="Confidence Score", value=f"{confidence * 100:.1f}%")
        else:
            # 5. Graceful failure for non-200 status
            st.warning(f"Server returned status code {response.status_code}. Make sure the FastAPI server is running properly.")

    except requests.exceptions.RequestException:
        # 5. Graceful failure if FastAPI server is not running
        st.warning("Could not connect to the API. Please start the FastAPI server first (`uvicorn main:app --reload`).")