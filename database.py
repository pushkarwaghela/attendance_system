"""
Database operations for attendance management - FIXED
"""

import csv
from datetime import datetime
import config

class AttendanceDB:
    def __init__(self):
        self.attendance_file = config.ATTENDANCE_FILE
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.marked_students = set()
        
        # Load today's attendance
        self.load_todays_attendance()
    
    def load_todays_attendance(self):
        """Load today's attendance records"""
        if self.attendance_file.exists():
            try:
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Date') == self.today:
                            name = row.get('Name', '')
                            if name:
                                self.marked_students.add(name)
            except Exception as e:
                print(f"Error loading attendance: {e}")
    
    def mark_attendance(self, name, method="Manual"):
        """Mark attendance for a student"""
        if name in self.marked_students:
            return False, f"{name} already marked present today"
        
        # Create record
        now = datetime.now()
        record = {
            'Name': name,
            'Date': self.today,
            'Time': now.strftime("%H:%M:%S"),
            'Method': method
        }
        
        # Save to CSV
        file_exists = self.attendance_file.exists()
        
        try:
            with open(self.attendance_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['Name', 'Date', 'Time', 'Method']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(record)
            
            # Update set
            self.marked_students.add(name)
            
            return True, f"✅ {name} marked present at {now.strftime('%H:%M:%S')}"
        
        except Exception as e:
            return False, f"Error saving attendance: {e}"
    
    def get_todays_attendance(self):
        """Get today's attendance as list of dicts"""
        today_records = []
        if self.attendance_file.exists():
            try:
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Date') == self.today:
                            today_records.append(row)
            except Exception:
                pass
        return today_records
    
    def get_attendance_summary(self, total_students):
        """Generate attendance summary"""
        present_count = len(self.marked_students)
        absent_count = total_students - present_count
        percentage = (present_count / total_students * 100) if total_students > 0 else 0
        
        return {
            'total': total_students,
            'present': present_count,
            'absent': absent_count,
            'percentage': round(percentage, 2),
            'date': self.today
        }

# Global instance
attendance_db = AttendanceDB()