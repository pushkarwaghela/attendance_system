"""
AI SMART ATTENDANCE SYSTEM - MAIN APPLICATION
Fully working with fixed error handling
"""

import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import os

# Import our modules
from face_utils import face_recognizer
from database import attendance_db
import config

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Attendance System",
    page_icon="🎓",
    layout="wide"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    .metric {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .success-box {
        background: #00b09b;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        animation: slideIn 0.5s;
    }
    .error-box {
        background: #f43b47;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'camera_running' not in st.session_state:
    st.session_state.camera_running = False
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'registration_message' not in st.session_state:
    st.session_state.registration_message = ""

# Auto-encode faces if dataset exists
if len(face_recognizer.get_student_list()) == 0:
    if any(config.DATASET_FOLDER.glob('*.jpg')):
        with st.spinner("🔄 Encoding faces from dataset..."):
            face_recognizer.encode_faces_from_dataset()
            st.rerun()

# ==================== HEADER ====================
st.markdown("""
<div class="main-title">
    <h1 style="font-size: 3rem;">🎓 AI SMART ATTENDANCE SYSTEM</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Real-Time Face Recognition with OpenCV</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🎯 NAVIGATION")
    page = st.radio("", ["📊 Dashboard", "📸 Face Recognition", "👥 Students", "📈 Reports"])
    
    st.markdown("---")
    
    # Quick stats
    students = face_recognizer.get_student_list()
    total = len(students)
    present = len(attendance_db.marked_students)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {total}")
        st.markdown("Total")
    with col2:
        st.markdown(f"### {present}")
        st.markdown("Present")
    
    if total > 0:
        percentage = (present / total) * 100
        st.progress(percentage / 100, text=f"Today: {percentage:.1f}%")
    
    st.markdown("---")
    st.markdown(f"**📅 {datetime.now().strftime('%B %d, %Y')}**")
    st.markdown(f"**⏰ {datetime.now().strftime('%I:%M %p')}**")

# ==================== DASHBOARD PAGE ====================
if page == "📊 Dashboard":
    st.markdown("## 📊 DASHBOARD")
    
    if total == 0:
        st.warning("⚠️ No students registered. Go to '👥 Students' tab to add students.")
    else:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric"><h3>Total</h3><h2>{total}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric" style="background: #00b09b"><h3>Present</h3><h2>{present}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric" style="background: #f43b47"><h3>Absent</h3><h2>{total - present}</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric" style="background: #f7971e"><h3>%</h3><h2>{percentage:.1f}%</h2></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Today's attendance
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Today's Attendance")
        today_records = attendance_db.get_todays_attendance()
        if today_records:
            # Convert to dataframe for better display
            import pandas as pd
            df = pd.DataFrame(today_records)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export button
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No attendance marked yet today")
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== FACE RECOGNITION PAGE ====================
elif page == "📸 Face Recognition":
    st.markdown("## 📸 FACE RECOGNITION")
    
    if total == 0:
        st.warning("⚠️ No students registered. Please add students first.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎥 Live Camera Feed")
            
            # Camera controls
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("▶️ START CAMERA", use_container_width=True):
                    st.session_state.camera_running = True
            with col_btn2:
                if st.button("⏹️ STOP CAMERA", use_container_width=True):
                    st.session_state.camera_running = False
            
            # Camera feed placeholder
            frame_placeholder = st.empty()
            status_placeholder = st.empty()
            
            if st.session_state.camera_running:
                # Initialize camera
                cap = cv2.VideoCapture(config.CAMERA_INDEX)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                
                if not cap.isOpened():
                    st.error("❌ Cannot access camera. Please check camera connection.")
                    st.session_state.camera_running = False
                else:
                    while st.session_state.camera_running:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed to capture frame")
                            break
                        
                        # Recognize faces
                        faces = face_recognizer.recognize_faces(frame)
                        
                        # Draw rectangles and names
                        for face in faces:
                            x, y, w, h = face['bbox']
                            name = face['name']
                            
                            # Choose color
                            if name != "Unknown":
                                color = (0, 255, 0)  # Green
                                if face['can_mark']:
                                    success, msg = attendance_db.mark_attendance(name, "Camera")
                                    if success:
                                        status_placeholder.success(f"✅ {name} marked present!")
                            else:
                                color = (0, 0, 255)  # Red
                            
                            # Draw rectangle
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                            
                            # Draw label background
                            label = f"{name}"
                            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                            cv2.rectangle(frame, (x, y - label_height - 10), (x + label_width, y), color, -1)
                            
                            # Draw label text
                            cv2.putText(frame, label, (x, y - 5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        
                        # Add info text
                        cv2.putText(frame, f"Faces Detected: {len(faces)}", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        # Convert to RGB for display
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_placeholder.image(frame_rgb, channels="RGB", width=config.CAMERA_WIDTH)
                        
                        time.sleep(0.03)
                    
                    cap.release()
            else:
                st.info("👆 Click 'START CAMERA' to begin face recognition")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Recently marked
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### ✅ Recently Marked")
            if attendance_db.marked_students:
                for name in sorted(attendance_db.marked_students)[-10:]:
                    st.markdown(f"• {name}")
            else:
                st.info("No students marked yet")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Manual entry
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📝 Manual Entry")
            with st.form("manual_form"):
                student = st.selectbox("Select Student", students)
                if st.form_submit_button("Mark Present", use_container_width=True):
                    success, msg = attendance_db.mark_attendance(student, "Manual")
                    if success:
                        st.success(msg)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning(msg)
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== STUDENTS PAGE ====================
elif page == "👥 Students":
    st.markdown("## 👥 STUDENT MANAGEMENT")
    
    # Show registration message if exists
    if st.session_state.registration_message:
        if st.session_state.registration_success:
            st.markdown(f'<div class="success-box">{st.session_state.registration_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{st.session_state.registration_message}</div>', unsafe_allow_html=True)
        st.session_state.registration_message = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Add New Student")
        
        with st.form("add_student_form"):
            name = st.text_input("Full Name", placeholder="Enter student name")
            photo = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png'], 
                                   help="Upload a clear face photo with good lighting")
            
            if st.form_submit_button("Register Student", use_container_width=True):
                if name and photo:
                    with st.spinner("🔄 Processing face..."):
                        success, message = face_recognizer.add_new_student(name, photo)
                        st.session_state.registration_success = success
                        st.session_state.registration_message = message
                        if success:
                            st.balloons()
                        time.sleep(2)
                        st.rerun()
                else:
                    st.session_state.registration_success = False
                    st.session_state.registration_message = "❌ Please provide both name and photo"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tips for good photos
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📸 Photo Tips")
        st.markdown("""
        - Use frontal face photo
        - Ensure good lighting
        - No sunglasses or masks
        - Clear background
        - Single person in frame
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Registered Students")
        
        if students:
            for student in students:
                status = "✅ Present" if student in attendance_db.marked_students else "❌ Absent"
                status_color = "#00b09b" if student in attendance_db.marked_students else "#f43b47"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                          padding: 0.5rem; background: #f8f9fa; border-radius: 5px; margin-bottom: 0.5rem;">
                    <span>{student}</span>
                    <span style="color: {status_color};">{status}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Re-encode button
            if st.button("🔄 Re-encode All Faces", use_container_width=True):
                with st.spinner("Encoding faces..."):
                    if face_recognizer.encode_faces_from_dataset():
                        st.success("✅ Faces re-encoded successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ No faces found in images")
        else:
            st.info("No students registered yet")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== REPORTS PAGE ====================
elif page == "📈 Reports":
    st.markdown("## 📈 ATTENDANCE REPORTS")
    
    if config.ATTENDANCE_FILE.exists():
        import csv
        import pandas as pd
        
        # Read all records
        records = []
        with open(config.ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        
        if records:
            # Get unique dates
            dates = sorted(set(r['Date'] for r in records), reverse=True)
            selected_date = st.selectbox("Select Date", dates)
            
            # Filter records
            filtered = [r for r in records if r['Date'] == selected_date]
            
            # Show summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric"><h3>Date</h3><h4>{selected_date}</h4></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric" style="background: #00b09b"><h3>Present</h3><h4>{len(filtered)}</h4></div>', unsafe_allow_html=True)
            with col3:
                total_students = len(students) if students else 0
                percentage = (len(filtered) / total_students * 100) if total_students > 0 else 0
                st.markdown(f'<div class="metric" style="background: #f7971e"><h3>%</h3><h4>{percentage:.1f}%</h4></div>', unsafe_allow_html=True)
            
            # Display records
            st.markdown('<div class="card">', unsafe_allow_html=True)
            df = pd.DataFrame(filtered)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export
            csv_data = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv_data, f"attendance_{selected_date}.csv", "text/csv", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No attendance records found")
    else:
        st.info("No attendance records found")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎓 AI Assisted Smart Attendance System | Amrutvahini College of Engineering</p>
    <p style='font-size: 0.8rem;'>Powered by OpenCV & Streamlit</p>
</div>
""", unsafe_allow_html=True)