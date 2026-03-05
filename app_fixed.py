"""
AI SMART ATTENDANCE SYSTEM - FINAL FIXED VERSION
Camera working perfectly during registration
"""

# Force numpy import first
import numpy as np
import pandas as pd
import cv2
import streamlit as st
import time
from datetime import datetime
from pathlib import Path
import os
import threading
import queue

from face_utils import face_recognizer
from database import attendance_db
import config

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Professional Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        color: white;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Metric Card */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Angle Badge */
    .angle-badge {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .angle-badge.completed {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border: none;
    }
    
    /* Student Card */
    .student-card {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        color: white;
        transition: all 0.3s;
    }
    
    .student-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(5px);
    }
    
    /* Status Badge */
    .status-present {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-absent {
        background: linear-gradient(135deg, #f43b47, #453a94);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Timer Circle */
    .timer-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
        border: 3px solid rgba(255, 255, 255, 0.3);
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .timer-number {
        font-size: 4rem;
        font-weight: 800;
        color: white;
    }
    
    /* Progress Bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #00b09b, #96c93d);
        height: 10px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Camera Container */
    .camera-container {
        border-radius: 15px;
        overflow: hidden;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, p, span, label {
        color: white !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    /* DataFrame */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CAMERA FUNCTIONS ====================
@st.cache_resource
def get_camera():
    """Get camera instance with proper initialization"""
    try:
        # Try multiple backends
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
            cap = cv2.VideoCapture(config.CAMERA_INDEX, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Test frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera initialized with backend: {backend}")
                    return cap
                cap.release()
        return None
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return None

def release_camera(cap):
    """Safely release camera"""
    if cap is not None:
        cap.release()

# ==================== SESSION STATE ====================
if 'capture_mode' not in st.session_state:
    st.session_state.capture_mode = False
if 'capture_count' not in st.session_state:
    st.session_state.capture_count = 0
if 'current_student' not in st.session_state:
    st.session_state.current_student = ""
if 'captured_angles' not in st.session_state:
    st.session_state.captured_angles = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'timer_value' not in st.session_state:
    st.session_state.timer_value = 3
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = True
if 'camera_instance' not in st.session_state:
    st.session_state.camera_instance = None
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'registration_message' not in st.session_state:
    st.session_state.registration_message = ""

# Initial encoding
if not face_recognizer.known_face_encodings:
    with st.spinner("📸 Loading faces from dataset..."):
        face_recognizer.encode_faces()

# ==================== HEADER ====================
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;
               background: linear-gradient(135deg, #fff, #f0f0f0);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🎓 AI ATTENDANCE SYSTEM
    </h1>
    <p style="font-size: 1.2rem; color: rgba(255,255,255,0.9);">
        Professional Face Recognition
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🎯 NAVIGATION")
    
    page = st.radio(
        "nav",
        ["📊 DASHBOARD", "📸 ATTENDANCE", "👥 REGISTER", "📈 REPORTS"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats
    students = face_recognizer.get_student_list()
    total = len(students)
    present = len(attendance_db.marked_students)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("TOTAL", total)
    with col2:
        st.metric("PRESENT", present)
    
    if total > 0:
        progress = present / total
        st.progress(progress, text=f"Today: {progress*100:.1f}%")
    
    st.markdown("---")
    
    # Time
    now = datetime.now()
    st.markdown(f"**📅 {now.strftime('%B %d, %Y')}**")
    st.markdown(f"**⏰ {now.strftime('%I:%M %p')}**")

# ==================== DASHBOARD ====================
if page == "📊 DASHBOARD":
    st.markdown("## 📊 DASHBOARD")
    
    if total == 0:
        st.info("No students registered. Go to REGISTER tab.")
    else:
        # Metrics
        cols = st.columns(4)
        metrics = [
            ("TOTAL", total, "#667eea"),
            ("PRESENT", present, "#00b09b"),
            ("ABSENT", total - present, "#f43b47"),
            ("PERCENTAGE", f"{(present/total)*100:.1f}%", "#f7971e")
        ]
        
        for col, (label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color}, {color}dd);">
                    <h3 style="font-size: 1rem;">{label}</h3>
                    <h2 style="font-size: 2.5rem;">{value}</h2>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Today's attendance
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 TODAY'S ATTENDANCE")
        
        records = attendance_db.get_todays_attendance()
        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 EXPORT CSV", csv, f"attendance_{datetime.now():%Y%m%d}.csv", "text/csv")
        else:
            st.info("No attendance marked yet")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== ATTENDANCE ====================
elif page == "📸 ATTENDANCE":
    st.markdown("## 📸 MARK ATTENDANCE")
    
    if total == 0:
        st.warning("⚠️ Register students first")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🎥 LIVE CAMERA")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("▶️ START", use_container_width=True):
                    st.session_state.camera_active = True
            with col_btn2:
                if st.button("⏹️ STOP", use_container_width=True):
                    st.session_state.camera_active = False
            
            feed = st.empty()
            status = st.empty()
            
            if st.session_state.camera_active:
                cap = get_camera()
                
                if cap is None:
                    st.error("❌ Cannot access camera")
                    st.session_state.camera_active = False
                else:
                    stop_btn = st.button("⏹️ STOP", key="stop_cam")
                    
                    while st.session_state.camera_active and not stop_btn:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Fast recognition
                        faces = face_recognizer.recognize_faces(frame)
                        
                        for face in faces:
                            x, y, w, h = face['bbox']
                            name = face['name']
                            conf = face['confidence']
                            
                            if name != "Unknown":
                                color = (0, 255, 0)
                                if face['can_mark']:
                                    success, msg = attendance_db.mark_attendance(name, "Camera")
                                    if success:
                                        status.success(f"✅ {name}")
                            else:
                                color = (0, 0, 255)
                            
                            # Draw
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                            cv2.putText(frame, f"{name} ({conf:.0f}%)", (x, y-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        feed.image(frame_rgb, channels="RGB", width=config.CAMERA_WIDTH)
                        
                        if stop_btn:
                            break
                        
                        time.sleep(0.03)
                    
                    release_camera(cap)
                    st.session_state.camera_active = False
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### ✅ TODAY'S PRESENT")
            if attendance_db.marked_students:
                for name in sorted(attendance_db.marked_students):
                    st.markdown(f"• {name}")
            else:
                st.info("No marks yet")
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== REGISTER ====================
elif page == "👥 REGISTER":
    st.markdown("## 👥 REGISTER STUDENT")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📝 NEW STUDENT")
        
        with st.form("register"):
            name = st.text_input("Full Name").strip().upper()
            if st.form_submit_button("🎯 START CAPTURE", use_container_width=True):
                if name:
                    st.session_state.current_student = name
                    st.session_state.capture_mode = True
                    st.session_state.capture_count = 0
                    st.session_state.captured_angles = []
                    st.session_state.preview_mode = True
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Registered list
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 REGISTERED")
        if students:
            for student in students:
                angle_count = len(list(config.DATASET_FOLDER.glob(f"{student}_*.jpg")))
                status = "PRESENT" if student in attendance_db.marked_students else "ABSENT"
                status_class = "status-present" if status == "PRESENT" else "status-absent"
                
                st.markdown(f"""
                <div class="student-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{student}</strong><br>
                            <small>{angle_count} angles</small>
                        </div>
                        <span class="{status_class}">{status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No students")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.capture_mode:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"### 📸 CAPTURING: {st.session_state.current_student}")
            
            # Progress
            progress = st.session_state.capture_count / 5
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-fill" style="width: {progress*100}%;"></div>
            </div>
            <p style="text-align: center;">{st.session_state.capture_count}/5 ANGLES</p>
            """, unsafe_allow_html=True)
            
            # Angle badges
            angles = ["FRONT", "LEFT", "RIGHT", "UP", "DOWN"]
            cols = st.columns(5)
            for i, angle in enumerate(angles):
                with cols[i]:
                    if angle in st.session_state.captured_angles:
                        st.markdown(f'<div class="angle-badge completed">✅ {angle}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="angle-badge">⏳ {angle}</div>', unsafe_allow_html=True)
            
            # Camera capture section - FIXED to show camera feed
            if st.session_state.capture_count < 5:
                current_angle = angles[st.session_state.capture_count]
                
                # Camera feed placeholder
                camera_placeholder = st.empty()
                
                # Get camera instance
                cap = get_camera()
                
                if cap is None:
                    st.error("❌ Cannot access camera")
                else:
                    if st.session_state.preview_mode:
                        # PREVIEW MODE - Show live feed with instructions
                        ret, frame = cap.read()
                        if ret:
                            # Add instructions to frame
                            cv2.putText(frame, f"ANGLE: {current_angle}", (10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.putText(frame, "Position your face", (10, 60),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            cv2.putText(frame, "Click CAPTURE when ready", (10, 90),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            camera_placeholder.image(frame_rgb, channels="RGB", width=config.CAMERA_WIDTH)
                            
                            # Capture button
                            if st.button(f"📸 CAPTURE {current_angle}", use_container_width=True):
                                st.session_state.preview_mode = False
                                st.session_state.timer_value = 3
                                st.rerun()
                    
                    else:
                        # COUNTDOWN MODE - Show countdown and capture
                        if st.session_state.timer_value > 0:
                            # Show timer
                            st.markdown(f"""
                            <div class="timer-circle">
                                <span class="timer-number">{st.session_state.timer_value}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show live feed with countdown
                            ret, frame = cap.read()
                            if ret:
                                cv2.putText(frame, f"Capturing in: {st.session_state.timer_value}", (10, 30),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                cv2.putText(frame, f"Hold still for {current_angle}", (10, 60),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                
                                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                camera_placeholder.image(frame_rgb, channels="RGB", width=config.CAMERA_WIDTH)
                                
                                # Countdown
                                time.sleep(1)
                                st.session_state.timer_value -= 1
                                st.rerun()
                        
                        else:
                            # CAPTURE MODE - Take photo
                            ret, frame = cap.read()
                            if ret:
                                # Save the image
                                success, msg = face_recognizer.add_student_angle(
                                    st.session_state.current_student, frame, current_angle.lower()
                                )
                                
                                if success:
                                    st.session_state.captured_angles.append(current_angle)
                                    st.session_state.capture_count += 1
                                    st.session_state.preview_mode = True
                                    st.session_state.timer_value = 3
                                    
                                    if st.session_state.capture_count == 5:
                                        with st.spinner("🔄 Encoding faces..."):
                                            face_recognizer.encode_faces()
                                        st.session_state.capture_mode = False
                                        st.balloons()
                                        st.success(f"✅ Student {st.session_state.current_student} registered successfully!")
                                    else:
                                        st.success(f"✅ {current_angle} captured!")
                                    
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    st.session_state.preview_mode = True
                                    st.rerun()
                    
                    # Release camera
                    release_camera(cap)
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== REPORTS ====================
elif page == "📈 REPORTS":
    st.markdown("## 📈 ATTENDANCE REPORTS")
    
    if config.ATTENDANCE_FILE.exists():
        try:
            df = pd.read_csv(config.ATTENDANCE_FILE)
            if not df.empty:
                dates = sorted(df['Date'].unique(), reverse=True)
                selected = st.selectbox("SELECT DATE", dates)
                
                filtered = df[df['Date'] == selected]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("DATE", selected)
                with col2:
                    st.metric("PRESENT", len(filtered))
                with col3:
                    pct = (len(filtered) / total * 100) if total > 0 else 0
                    st.metric("PERCENTAGE", f"{pct:.1f}%")
                
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                
                csv = filtered.to_csv(index=False)
                st.download_button("📥 DOWNLOAD CSV", csv, f"attendance_{selected}.csv", "text/csv")
            else:
                st.info("No records")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("No records")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: rgba(255,255,255,0.8);">
    <p>🎓 AI INNOVATION SPRINT | AMRUTVAHINI COLLEGE OF ENGINEERING</p>
</div>
""", unsafe_allow_html=True)