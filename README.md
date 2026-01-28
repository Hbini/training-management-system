# Advanced Training Management System (ATMS)

A robust, enterprise-grade Python solution for managing educational institutions, corporate training programs, and online courses.

## 🚀 Features

### 👤 Student Management
- **Complete Profile:** Store personal details, contact info, and registration history.
- **Validation:** Built-in validation for Email, Phone, and Brazilian CPF.
- **Search & Filter:** Easily find students by name, email, or status.
- **Activity Logging:** Track every change made to student records.

### 📚 Course Catalog
- **Detailed Metadata:** Manage duration, categories, instructors, and prerequisites.
- **Capacity Control:** Automatic tracking of available seats and max enrollment.
- **Pricing:** Support for course fees and financial tracking.

### 📝 Enrollments & Progress
- **Lifecycle Tracking:** Manage enrollment from registration to completion/graduation.
- **Progress Monitoring:** Real-time updates on student progress percentages.
- **Attendance System:** Record and track student presence in classes.
- **Grading:** Record assessment scores and calculate average grades.

### 🎓 Certification
- **Auto-Generation:** Generate unique certificates for students who complete courses.
- **Verification System:** Secure verification codes to validate certificate authenticity.
- **History:** Keep a record of all issued certifications.

### 📊 Reporting & Analytics
- **Course Stats:** Get instant insights into enrollment counts, status breakdowns, and average performance.
- **Data Export:** Export detailed enrollment reports to CSV for external analysis.
- **System Logs:** Full audit trail of all administrative actions.

## 🛠️ Technical Stack
- **Language:** Python 3.8+
- **Database:** SQLite (with advanced connection management)
- **Architecture:** Modular Class-based design (Managers, Models, Validators)
- **Persistence:** Local DB file with automatic table initialization

## 📖 How to Use

1. **Prerequisites:** Ensure you have Python installed.
2. **Run:** Execute `python main.py` to start the interactive CLI.
3. **Database:** The system will automatically create `training_management.db` on first run.

### CLI Menu Structure:
- **1. Students:** Add, list, or search for students.
- **2. Courses:** Manage the course catalog and check availability.
- **3. Enrollments:** Register students for courses and update their progress.
- **4. Reports:** View statistics, export data, and issue certificates.

---
*Developed as part of an advanced Python development challenge.*
