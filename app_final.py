"""
AI SMART ATTENDANCE SYSTEM - FINAL WORKING VERSION
Perfect face recognition with multi-angle registration
"""

import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import pandas as pd
from pathlib import Path
import os

from face_utils import face_recognizer

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Attendance",
    page_icon="🎓",
    layout="wide"
)

# ==================== DATABASE ====================
class AttendanceDB:
    def __init__(self):
        self.file = Path("attendance.csv")
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.marked = set()
        self.load()
    
    def load(self):
        if self.file.exists():
            df = pd.read_csv(self.file)
            today_df = df[df['Date'] == self.today] if 'Date' in df.columns else pd.DataFrame()
            self.marked = set(today_df['Name'].tolist()) if not today_df.empty else set()
    
    def mark(self, name, method="Camera"):
        if name in self.marked:
            return False, f"{name} already marked"
        
        now = datetime.now()
        record = {
            'Name': name,
            'Date': self.today,
            'Time': now.strftime("%H:%M:%S"),
            'Method': method
        }
        
        df = pd.DataFrame([record])
        if self.file.exists():
            old_df = pd.read_csv(self.file)
            df = pd.concat([old_df, df], ignore_index=True)
        df.to_csv(self.file, index=False)
        
        self.marked.add(name)
        return True, f"✅ {name} marked at {now.strftime('%H:%M:%S')}"
    
    def get_today(self):
        if self.file.exists():
            df = pd.read_csv(self.file)
            return df[df['Date'] == self.today] if 'Date' in df.columns else pd.DataFrame()
        return pd.DataFrame()

db = AttendanceDB()

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .angle-badge {
        background: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        display: inline-block;
        margin: 0.2rem;
    }
    .angle-badge.completed {
        background: #00b09b;
        color: white;
    }
    .camera-box {
        border: 3px solid #667eea;
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .timer-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        border-radius: 50%;
        width: 150px;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1rem auto;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .confidence-badge {
        background: #667eea;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'reg_mode' not in st.session_state:
    st.session_state.reg_mode = False
if 'reg_name' not in st.session_state:
    st.session_state.reg_name = ""
if 'reg_angles' not in st.session_state:
    st.session_state.reg_angles = []
if 'reg_count' not in st.session_state:
    st.session_state.reg_count = 0
if 'preview' not in st.session_state:
    st.session_state.preview = True
if 'timer' not in st.session_state:
    st.session_state.timer = 3
if 'cam_active' not in st.session_state:
    st.session_state.cam_active = False

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>🎓 AI ATTENDANCE SYSTEM</h1>
    <p>Professional Face Recognition with Multi-Angle Registration</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🎯 MENU")
    if st.button("📊 DASHBOARD", use_container_width=True):
        st.session_state.page = "dashboard"
    if st.button("📸 ATTENDANCE", use_container_width=True):
        st.session_state.page = "attendance"
    if st.button("👥 REGISTER", use_container_width=True):
        st.session_state.page = "register"
    if st.button("📈 REPORTS", use_container_width=True):
        st.session_state.page = "reports"
    
    st.markdown("---")
    students = face_recognizer.get_students()
    total = len(students)
    present = len(db.marked)
    
    st.metric("TOTAL STUDENTS", total)
    st.metric("PRESENT TODAY", present)
    if total > 0:
        st.progress(present/total, text=f"{(present/total)*100:.1f}%")
    
    st.markdown(f"**📅 {datetime.now().strftime('%B %d, %Y')}**")
    st.markdown(f"**⏰ {datetime.now().strftime('%I:%M %p')}**")

# ==================== DASHBOARD ====================
if st.session_state.page == "dashboard":
    st.markdown("## 📊 DASHBOARD")
    
    if total == 0:
        st.info("No students registered. Go to REGISTER tab.")
    else:
        cols = st.columns(4)
        metrics = [
            ("TOTAL", total),
            ("PRESENT", present),
            ("ABSENT", total - present),
            ("PERCENTAGE", f"{(present/total)*100:.1f}%")
        ]
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.markdown(f'<div class="metric-card"><h3>{label}</h3><h2>{value}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📋 Today's Attendance")
        today_df = db.get_today()
        if not today_df.empty:
            st.dataframe(today_df, use_container_width=True)
        else:
            st.info("No attendance marked yet")

# ==================== ATTENDANCE ====================
elif st.session_state.page == "attendance":
    st.markdown("## 📸 MARK ATTENDANCE")
    
    if total == 0:
        st.warning("Register students first")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎥 Camera Feed")
            
            if st.button("▶️ START CAMERA", use_container_width=True):
                st.session_state.cam_active = True
            
            if st.session_state.cam_active:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    stop = st.button("⏹️ STOP", key="stop_attendance")
                    frame_placeholder = st.empty()
                    status = st.empty()
                    
                    while st.session_state.cam_active and not stop:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        # Recognize faces
                        faces = face_recognizer.recognize_faces(frame)
                        
                        for face in faces:
                            x, y, w, h = face['bbox']
                            name = face['name']
                            conf = face['confidence']
                            
                            if name != "Unknown":
                                color = (0, 255, 0)
                                if face['can_mark']:
                                    success, msg = db.mark(name)
                                    if success:
                                        status.success(msg)
                            else:
                                color = (0, 0, 255)
                            
                            # Draw rectangle
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                            
                            # Draw name with confidence
                            label = f"{name} ({conf:.1f}%)"
                            cv2.putText(frame, label, (x, y-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_placeholder.image(frame_rgb, channels="RGB", width=640)
                        
                        if stop:
                            st.session_state.cam_active = False
                            break
                        
                        time.sleep(0.03)
                    
                    cap.release()
                    st.rerun()
                else:
                    st.error("Cannot access camera")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### ✅ Today's Present")
            if db.marked:
                for name in sorted(db.marked):
                    st.markdown(f"• {name}")
            else:
                st.info("No marks yet")
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== REGISTER ====================
elif st.session_state.page == "register":
    st.markdown("## 👥 REGISTER STUDENT")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 New Student")
        
        name = st.text_input("Full Name").strip().upper()
        if st.button("🎯 START REGISTRATION", use_container_width=True):
            if name:
                st.session_state.reg_mode = True
                st.session_state.reg_name = name
                st.session_state.reg_angles = []
                st.session_state.reg_count = 0
                st.session_state.preview = True
                st.session_state.timer = 3
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Registered Students")
        if students:
            for student in students:
                st.markdown(f"• {student}")
        else:
            st.info("No students")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.reg_mode:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 📸 Capturing: {st.session_state.reg_name}")
            
            # Progress
            progress = st.session_state.reg_count / 5
            st.progress(progress, text=f"{st.session_state.reg_count}/5 angles")
            
            # Angle badges
            angles = ["FRONT", "LEFT", "RIGHT", "UP", "DOWN"]
            cols = st.columns(5)
            for i, angle in enumerate(angles):
                with cols[i]:
                    if angle in st.session_state.reg_angles:
                        st.markdown(f'<div class="angle-badge completed">✅ {angle}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="angle-badge">⏳ {angle}</div>', unsafe_allow_html=True)
            
            # Camera capture
            if st.session_state.reg_count < 5:
                current_angle = angles[st.session_state.reg_count]
                
                # Initialize camera
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    st.error("❌ Cannot access camera")
                else:
                    if st.session_state.preview:
                        # PREVIEW MODE - Show live feed
                        ret, frame = cap.read()
                        if ret:
                            # Add instructions
                            cv2.putText(frame, f"ANGLE: {current_angle}", (10, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            cv2.putText(frame, "Click CAPTURE when ready", (10, 60),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            # Show camera feed
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            st.image(frame_rgb, channels="RGB", width=640)
                            
                            # Capture button
                            if st.button(f"📸 CAPTURE {current_angle}", use_container_width=True):
                                st.session_state.preview = False
                                st.session_state.timer = 3
                                st.rerun()
                    
                    else:
                        if st.session_state.timer > 0:
                            # COUNTDOWN MODE
                            st.markdown(f'<div class="timer-box">{st.session_state.timer}</div>', unsafe_allow_html=True)
                            
                            ret, frame = cap.read()
                            if ret:
                                cv2.putText(frame, f"Capturing in: {st.session_state.timer}", (10, 30),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                
                                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                st.image(frame_rgb, channels="RGB", width=640)
                                
                                time.sleep(1)
                                st.session_state.timer -= 1
                                st.rerun()
                        
                        else:
                            # CAPTURE MODE
                            ret, frame = cap.read()
                            if ret:
                                success, msg = face_recognizer.add_student_angle(
                                    st.session_state.reg_name, frame, current_angle.lower()
                                )
                                
                                if success:
                                    st.session_state.reg_angles.append(current_angle)
                                    st.session_state.reg_count += 1
                                    st.session_state.preview = True
                                    st.session_state.timer = 3
                                    
                                    if st.session_state.reg_count == 5:
                                        st.session_state.reg_mode = False
                                        st.balloons()
                                        st.success(f"✅ {st.session_state.reg_name} registered with 5 angles!")
                                    else:
                                        st.success(f"✅ {current_angle} captured!")
                                    
                                    st.rerun()
                                else:
                                    st.error(msg)
                                    st.session_state.preview = True
                                    st.rerun()
                    
                    cap.release()
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== REPORTS ====================
elif st.session_state.page == "reports":
    st.markdown("## 📈 ATTENDANCE REPORTS")
    
    if Path("attendance.csv").exists():
        df = pd.read_csv("attendance.csv")
        if not df.empty:
            dates = sorted(df['Date'].unique(), reverse=True)
            selected = st.selectbox("Select Date", dates)
            
            filtered = df[df['Date'] == selected]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date", selected)
            with col2:
                st.metric("Present", len(filtered))
            with col3:
                pct = (len(filtered) / total * 100) if total > 0 else 0
                st.metric("Percentage", f"{pct:.1f}%")
            
            st.dataframe(filtered, use_container_width=True)
            
            csv = filtered.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, f"attendance_{selected}.csv", "text/csv")
        else:
            st.info("No records")
    else:
        st.info("No records")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎓 AI INNOVATION SPRINT | AMRUTVAHINI COLLEGE OF ENGINEERING</p>
</div>
""", unsafe_allow_html=True)