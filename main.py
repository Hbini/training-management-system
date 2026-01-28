#!/usr/bin/env python3
"""
Training Management System - Complete Solution
A comprehensive Python system for managing training courses, students, 
enrollments, progress tracking, certifications, and reporting.

Features:
- Student management with validation
- Course catalog management
- Enrollment and attendance tracking
- Progress monitoring and grading
- Certification generation
- Advanced reporting and analytics
- Data export capabilities

Author: Hbini
Version: 2.0.0
Date: January 28, 2026
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
import hashlib
import secrets
from dataclasses import dataclass, asdict
from enum import Enum
import os


# ============= ENUMERATIONS =============

class StudentStatus(Enum):
    """Student status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"


class EnrollmentStatus(Enum):
    """Enrollment status enumeration"""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"
    FAILED = "failed"


class CourseCategory(Enum):
    """Course category enumeration"""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    DESIGN = "design"
    MARKETING = "marketing"
    DATA_SCIENCE = "data_science"
    SOFT_SKILLS = "soft_skills"
    OTHER = "other"


# ============= DATA CLASSES =============

@dataclass
class Student:
    """Student data class"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[str] = None
    registration_date: str = ""
    status: str = StudentStatus.ACTIVE.value
    notes: Optional[str] = None


@dataclass  
class Course:
    """Course data class"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    duration_hours: int = 0
    category: str = CourseCategory.OTHER.value
    instructor: str = ""
    prerequisites: Optional[str] = None
    max_students: int = 30
    price: float = 0.0
    created_date: str = ""
    is_active: bool = True


@dataclass
class Enrollment:
    """Enrollment data class"""
    id: Optional[int] = None
    student_id: int = 0
    course_id: int = 0
    enrollment_date: str = ""
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    expected_completion: Optional[str] = None
    progress: float = 0.0
    status: str = EnrollmentStatus.ENROLLED.value
    grade: Optional[float] = None
    attendance_percentage: float = 0.0
    feedback: Optional[str] = None


# ============= DATABASE MANAGER =============

class DatabaseManager:
    """Advanced database management with connection pooling"""
    
    def __init__(self, db_path: str = "training_management.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize_database(self):
        """Initialize all database tables with proper schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                cpf TEXT UNIQUE,
                birth_date TEXT,
                registration_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT,
                duration_hours INTEGER NOT NULL,
                category TEXT DEFAULT 'other',
                instructor TEXT,
                prerequisites TEXT,
                max_students INTEGER DEFAULT 30,
                price REAL DEFAULT 0.0,
                is_active BOOLEAN DEFAULT 1,
                created_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Enrollments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TEXT NOT NULL,
                start_date TEXT,
                completion_date TEXT,
                expected_completion TEXT,
                progress REAL DEFAULT 0.0,
                status TEXT DEFAULT 'enrolled',
                grade REAL,
                attendance_percentage REAL DEFAULT 0.0,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
        """)
        
        # Certifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL,
                certificate_number TEXT UNIQUE NOT NULL,
                issue_date TEXT NOT NULL,
                expiry_date TEXT,
                verification_code TEXT UNIQUE NOT NULL,
                certificate_url TEXT,
                issued_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (enrollment_id) REFERENCES enrollments (id) ON DELETE CASCADE
            )
        """)
        
        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL,
                class_date TEXT NOT NULL,
                present BOOLEAN NOT NULL DEFAULT 0,
                justification TEXT,
                notes TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (enrollment_id) REFERENCES enrollments (id) ON DELETE CASCADE
            )
        """)
        
        # Assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL,
                assessment_type TEXT NOT NULL,
                assessment_date TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (enrollment_id) REFERENCES enrollments (id) ON DELETE CASCADE
            )
        """)
        
        # Activity logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_type TEXT NOT NULL,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✓ Database initialized successfully")
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[sqlite3.Cursor]:
        """Execute query with error handling"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            return None
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch single row as dictionary"""
        cursor = self.execute_query(query, params)
        if cursor:
            row = cursor.fetchone()
            return dict(row) if row else None
        return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows as list of dictionaries"""
        cursor = self.execute_query(query, params)
        if cursor:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        return []
    
    def log_activity(self, user_type: str, user_id: int, action: str, details: str = None):
        """Log system activity"""
        query = "INSERT INTO activity_logs (user_type, user_id, action, details) VALUES (?, ?, ?, ?)"
        self.execute_query(query, (user_type, user_id, action, details))
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("✓ Database connection closed")


# ============= VALIDATION UTILITIES =============

class Validator:
    """Input validation and sanitization utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Brazilian phone format"""
        clean_phone = re.sub(r'[^0-9]', '', phone)
        return len(clean_phone) in [10, 11]  # Brazilian format
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Validate Brazilian CPF number"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Validate first digit
        sum_val = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = (sum_val * 10 % 11) % 10
        if int(cpf[9]) != digit1:
            return False
        
        # Validate second digit  
        sum_val = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = (sum_val * 10 % 11) % 10
        return int(cpf[10]) == digit2
    
    @staticmethod
    def validate_grade(grade: float) -> bool:
        """Validate grade range (0-100)"""
        return 0.0 <= grade <= 100.0
    
    @staticmethod
    def validate_progress(progress: float) -> bool:
        """Validate progress percentage (0-100)"""
        return 0.0 <= progress <= 100.0
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize text input"""
        return text.strip() if text else ""


# ============= STUDENT MANAGER =============

class StudentManager:
    """Comprehensive student management system"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def add_student(self, student: Student) -> Optional[int]:
        """Add new student with validation"""
        # Validate email
        if not Validator.validate_email(student.email):
            print("✗ Invalid email format")
            return None
        
        # Validate phone if provided
        if student.phone and not Validator.validate_phone(student.phone):
            print("✗ Invalid phone format")
            return None
        
        # Validate CPF if provided
        if student.cpf and not Validator.validate_cpf(student.cpf):
            print("✗ Invalid CPF")
            return None
        
        student.registration_date = datetime.now().isoformat()
        
        query = """
            INSERT INTO students (name, email, phone, cpf, birth_date, registration_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query, 
            (student.name, student.email, student.phone, student.cpf, 
             student.birth_date, student.registration_date, student.status, student.notes)
        )
        
        if cursor:
            student_id = cursor.lastrowid
            self.db.log_activity('student', student_id, 'CREATED', f'Student {student.name} registered')
            print(f"✓ Student '{student.name}' added successfully (ID: {student_id})")
            return student_id
        return None
    
    def get_student(self, student_id: int) -> Optional[Student]:
        """Get student by ID"""
        query = "SELECT * FROM students WHERE id = ?"
        result = self.db.fetch_one(query, (student_id,))
        
        if result:
            return Student(**{k: v for k, v in result.items() if k in Student.__annotations__})
        return None
    
    def get_student_by_email(self, email: str) -> Optional[Student]:
        """Get student by email"""
        query = "SELECT * FROM students WHERE email = ?"
        result = self.db.fetch_one(query, (email,))
        
        if result:
            return Student(**{k: v for k, v in result.items() if k in Student.__annotations__})
        return None
    
    def update_student(self, student_id: int, **kwargs) -> bool:
        """Update student information"""
        allowed_fields = ['name', 'email', 'phone', 'cpf', 'birth_date', 'status', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            print("✗ No valid fields to update")
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE students SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        cursor = self.db.execute_query(query, (*updates.values(), student_id))
        if cursor and cursor.rowcount > 0:
            self.db.log_activity('student', student_id, 'UPDATED', f'Fields: {list(updates.keys())}')
            print(f"✓ Student updated successfully")
            return True
        return False
    
    def delete_student(self, student_id: int) -> bool:
        """Soft delete student (set status to inactive)"""
        return self.update_student(student_id, status=StudentStatus.INACTIVE.value)
    
    def list_students(self, status: Optional[str] = None, limit: int = 100) -> List[Student]:
        """List students with optional status filter"""
        if status:
            query = "SELECT * FROM students WHERE status = ? ORDER BY name LIMIT ?"
            results = self.db.fetch_all(query, (status, limit))
        else:
            query = "SELECT * FROM students ORDER BY name LIMIT ?"
            results = self.db.fetch_all(query, (limit,))
        
        return [Student(**{k: v for k, v in row.items() if k in Student.__annotations__}) for row in results]
    
    def search_students(self, search_term: str) -> List[Student]:
        """Search students by name or email"""
        query = """
            SELECT * FROM students 
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY name
        """
        pattern = f"%{search_term}%"
        results = self.db.fetch_all(query, (pattern, pattern))
        
        return [Student(**{k: v for k, v in row.items() if k in Student.__annotations__}) for row in results]


# ============= COURSE MANAGER =============

class CourseManager:
    """Comprehensive course management system"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def add_course(self, course: Course) -> Optional[int]:
        """Add new course"""
        if course.duration_hours <= 0:
            print("✗ Invalid course duration")
            return None
        
        if course.price < 0:
            print("✗ Invalid price")
            return None
        
        course.created_date = datetime.now().isoformat()
        
        query = """
            INSERT INTO courses (title, description, duration_hours, category, instructor,
                               prerequisites, max_students, price, is_active, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query,
            (course.title, course.description, course.duration_hours, course.category,
             course.instructor, course.prerequisites, course.max_students, course.price,
             course.is_active, course.created_date)
        )
        
        if cursor:
            course_id = cursor.lastrowid
            self.db.log_activity('course', course_id, 'CREATED', f'Course {course.title} created')
            print(f"✓ Course '{course.title}' added successfully (ID: {course_id})")
            return course_id
        return None
    
    def get_course(self, course_id: int) -> Optional[Course]:
        """Get course by ID"""
        query = "SELECT * FROM courses WHERE id = ?"
        result = self.db.fetch_one(query, (course_id,))
        
        if result:
            return Course(**{k: v for k, v in result.items() if k in Course.__annotations__})
        return None
    
    def update_course(self, course_id: int, **kwargs) -> bool:
        """Update course information"""
        allowed_fields = ['title', 'description', 'duration_hours', 'category', 
                         'instructor', 'prerequisites', 'max_students', 'price', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE courses SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        cursor = self.db.execute_query(query, (*updates.values(), course_id))
        if cursor and cursor.rowcount > 0:
            self.db.log_activity('course', course_id, 'UPDATED', f'Fields: {list(updates.keys())}')
            print(f"✓ Course updated successfully")
            return True
        return False
    
    def list_courses(self, category: Optional[str] = None, active_only: bool = True) -> List[Course]:
        """List courses with optional filters"""
        if category:
            query = "SELECT * FROM courses WHERE category = ? AND is_active = ? ORDER BY title"
            results = self.db.fetch_all(query, (category, active_only))
        elif active_only:
            query = "SELECT * FROM courses WHERE is_active = 1 ORDER BY title"
            results = self.db.fetch_all(query)
        else:
            query = "SELECT * FROM courses ORDER BY title"
            results = self.db.fetch_all(query)
        
        return [Course(**{k: v for k, v in row.items() if k in Course.__annotations__}) for row in results]
    
    def get_available_seats(self, course_id: int) -> int:
        """Get number of available seats in a course"""
        course = self.get_course(course_id)
        if not course:
            return 0
        
        query = """
            SELECT COUNT(*) as enrolled 
            FROM enrollments 
            WHERE course_id = ? AND status IN ('enrolled', 'in_progress')
        """
        result = self.db.fetch_one(query, (course_id,))
        enrolled = result['enrolled'] if result else 0
        
        return max(0, course.max_students - enrolled)


# ============= ENROLLMENT MANAGER =============

class EnrollmentManager:
    """Comprehensive enrollment management system"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def enroll_student(self, student_id: int, course_id: int) -> Optional[int]:
        """Enroll student in a course"""
        # Check if seats are available
        course_mgr = CourseManager(self.db)
        available_seats = course_mgr.get_available_seats(course_id)
        
        if available_seats <= 0:
            print("✗ No seats available in this course")
            return None
        
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            enrollment_date=datetime.now().isoformat(),
            status=EnrollmentStatus.ENROLLED.value
        )
        
        # Calculate expected completion (assuming 3 months)
        expected = datetime.now() + timedelta(days=90)
        enrollment.expected_completion = expected.isoformat()
        
        query = """
            INSERT INTO enrollments (student_id, course_id, enrollment_date, expected_completion, status)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query,
            (enrollment.student_id, enrollment.course_id, enrollment.enrollment_date,
             enrollment.expected_completion, enrollment.status)
        )
        
        if cursor:
            enrollment_id = cursor.lastrowid
            self.db.log_activity('enrollment', enrollment_id, 'CREATED', 
                               f'Student {student_id} enrolled in course {course_id}')
            print(f"✓ Student enrolled successfully (Enrollment ID: {enrollment_id})")
            return enrollment_id
        return None
    
    def update_progress(self, enrollment_id: int, progress: float) -> bool:
        """Update enrollment progress"""
        if not Validator.validate_progress(progress):
            print("✗ Invalid progress value (must be 0-100)")
            return False
        
        # Auto-update status based on progress
        status = EnrollmentStatus.IN_PROGRESS.value
        if progress >= 100:
            status = EnrollmentStatus.COMPLETED.value
        
        query = """
            UPDATE enrollments 
            SET progress = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        cursor = self.db.execute_query(query, (progress, status, enrollment_id))
        
        if cursor and cursor.rowcount > 0:
            self.db.log_activity('enrollment', enrollment_id, 'PROGRESS_UPDATED', f'Progress: {progress}%')
            print(f"✓ Progress updated to {progress}%")
            return True
        return False
    def list_enrollments(self, course_id: Optional[int] = None) -> List[Dict]:
        """List all enrollments for a course with student details"""
        if course_id:
            query = """
                SELECT e.*, s.name as student_name, c.title as course_title
                FROM enrollments e
                JOIN students s ON e.student_id = s.id
                JOIN courses c ON e.course_id = c.id
                WHERE e.course_id = ?
            """
            return self.db.fetch_all(query, (course_id,))
        else:
            query = """
                SELECT e.*, s.name as student_name, c.title as course_title
                FROM enrollments e
                JOIN students s ON e.student_id = s.id
                JOIN courses c ON e.course_id = c.id
            """
            return self.db.fetch_all(query)


# ============= CERTIFICATION MANAGER =============

class CertificationManager:
    """System for generating and verifying certificates"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def generate_certificate(self, enrollment_id: int, issued_by: str = "Training System") -> Optional[str]:
        """Generate certificate for completed enrollment"""
        # Check if enrollment is completed
        query = "SELECT * FROM enrollments WHERE id = ? AND status = 'completed'"
        enrollment = self.db.fetch_one(query, (enrollment_id,))
        
        if not enrollment:
            print("✗ Enrollment not completed or not found")
            return None
        
        # Generate unique numbers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        cert_number = f"CERT-{enrollment_id}-{timestamp}"
        verify_code = secrets.token_hex(8).upper()
        issue_date = datetime.now().isoformat()
        
        query = """
            INSERT INTO certifications (enrollment_id, certificate_number, issue_date, 
                                      verification_code, issued_by)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query, (enrollment_id, cert_number, issue_date, verify_code, issued_by)
        )
        
        if cursor:
            self.db.log_activity('certification', cursor.lastrowid, 'ISSUED', 
                               f'Certificate {cert_number} issued for enrollment {enrollment_id}')
            print(f"✓ Certificate generated: {cert_number}")
            return cert_number
        return None
    
    def verify_certificate(self, verification_code: str) -> Optional[Dict]:
        """Verify certificate validity"""
        query = """
            SELECT cert.*, s.name as student_name, c.title as course_title
            FROM certifications cert
            JOIN enrollments e ON cert.enrollment_id = e.id
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            WHERE cert.verification_code = ?
        """
        return self.db.fetch_one(query, (verification_code,))


# ============= REPORTING SYSTEM =============

class ReportingSystem:
    """Advanced reporting and analytics system"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_course_statistics(self, course_id: int) -> Dict:
        """Get detailed statistics for a course"""
        stats = {}
        
        # Total enrolled
        query = "SELECT COUNT(*) as total FROM enrollments WHERE course_id = ?"
        stats['total_students'] = self.db.fetch_one(query, (course_id,))['total']
        
        # Status breakdown
        query = "SELECT status, COUNT(*) as count FROM enrollments WHERE course_id = ? GROUP BY status"
        stats['status_breakdown'] = {row['status']: row['count'] for row in self.db.fetch_all(query, (course_id,))}
        
        # Average grade
        query = "SELECT AVG(grade) as avg_grade FROM enrollments WHERE course_id = ? AND grade IS NOT NULL"
        result = self.db.fetch_one(query, (course_id,))
        stats['average_grade'] = round(result['avg_grade'], 2) if result['avg_grade'] else 0.0
        
        # Average progress
        query = "SELECT AVG(progress) as avg_progress FROM enrollments WHERE course_id = ?"
        result = self.db.fetch_one(query, (course_id,))
        stats['average_progress'] = round(result['avg_progress'], 2) if result['avg_progress'] else 0.0
        
        return stats
    
    def export_enrollments_to_csv(self, course_id: int, filename: str = "report.csv"):
        """Export enrollment data to CSV file"""
        query = """
            SELECT s.name, s.email, e.status, e.progress, e.grade
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id = ?
        """
        data = self.db.fetch_all(query, (course_id,))
        
        if not data:
            print("✗ No data to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✓ Report exported to {filename}")


# ============= MAIN APPLICATION CLI =============

def print_menu():
    """Print main menu options"""
    print("
" + "="*40)
    print("   TRAINING MANAGEMENT SYSTEM v2.0")
    print("="*40)
    print("1. Students Management")
    print("2. Courses Management")
    print("3. Enrollments & Progress")
    print("4. Reports & Certifications")
    print("0. Exit")
    print("-" * 40)

def main():
    """Main application loop"""
    db = DatabaseManager()
    student_mgr = StudentManager(db)
    course_mgr = CourseManager(db)
    enroll_mgr = EnrollmentManager(db)
    cert_mgr = CertificationManager(db)
    report_sys = ReportingSystem(db)
    
    try:
        while True:
            print_menu()
            choice = input("Select an option: ")
            
            if choice == '1':
                print("
[STUDENT MANAGEMENT]")
                print("1. Add Student
2. List Students
3. Search Student")
                sub = input("Select: ")
                if sub == '1':
                    name = input("Name: ")
                    email = input("Email: ")
                    phone = input("Phone: ")
                    student_mgr.add_student(Student(name=name, email=email, phone=phone))
                elif sub == '2':
                    for s in student_mgr.list_students():
                        print(f"ID: {s.id} | {s.name} ({s.email}) | Status: {s.status}")
                elif sub == '3':
                    term = input("Search term: ")
                    for s in student_mgr.search_students(term):
                        print(f"Found: {s.name} - {s.email}")
            
            elif choice == '2':
                print("
[COURSE MANAGEMENT]")
                print("1. Add Course
2. List Courses")
                sub = input("Select: ")
                if sub == '1':
                    title = input("Title: ")
                    hours = int(input("Hours: "))
                    course_mgr.add_course(Course(title=title, duration_hours=hours))
                elif sub == '2':
                    for c in course_mgr.list_courses():
                        print(f"ID: {c.id} | {c.title} ({c.duration_hours}h) | Seats: {course_mgr.get_available_seats(c.id)}")
            
            elif choice == '3':
                print("
[ENROLLMENT & PROGRESS]")
                print("1. Enroll Student
2. Update Progress
3. List Enrollments")
                sub = input("Select: ")
                if sub == '1':
                    sid = int(input("Student ID: "))
                    cid = int(input("Course ID: "))
                    enroll_mgr.enroll_student(sid, cid)
                elif sub == '2':
                    eid = int(input("Enrollment ID: "))
                    prog = float(input("Progress (0-100): "))
                    enroll_mgr.update_progress(eid, prog)
                elif sub == '3':
                    for e in enroll_mgr.list_enrollments():
                        print(f"EID: {e['id']} | {e['student_name']} -> {e['course_title']} | Progress: {e['progress']}%")
            
            elif choice == '4':
                print("
[REPORTS & CERTIFICATIONS]")
                print("1. Course Stats
2. Export to CSV
3. Generate Certificate")
                sub = input("Select: ")
                if sub == '1':
                    cid = int(input("Course ID: "))
                    print(json.dumps(report_sys.get_course_statistics(cid), indent=2))
                elif sub == '2':
                    cid = int(input("Course ID: "))
                    report_sys.export_enrollments_to_csv(cid)
                elif sub == '3':
                    eid = int(input("Enrollment ID: "))
                    cert_mgr.generate_certificate(eid)
            
            elif choice == '0':
                print("Exiting...")
                break
                
    finally:
        db.close()

if __name__ == "__main__":
    # If running for the first time, create sample data
    # (In a real scenario, this would be a separate setup script)
    main()
