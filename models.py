from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(10), unique=True, nullable=True)  # STU001-STU300
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admission_forms = db.relationship('AdmissionForm', backref='student', lazy=True)
    bonafide_forms = db.relationship('BonafideForm', backref='student', lazy=True)
    hostel_forms = db.relationship('HostelForm', backref='student', lazy=True)
    case_records = db.relationship('CaseRecord', backref='student', lazy=True)
    pratinidhan_forms = db.relationship('PratinidhanForm', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_student_id(self):
        if not self.student_id:
            # Find the highest existing STU ID
            from sqlalchemy import text
            last_user = User.query.filter(text("student_id LIKE 'STU%'")).order_by(text("student_id DESC")).first()
            if last_user and last_user.student_id:
                last_num = int(last_user.student_id[3:])
                new_num = last_num + 1
            else:
                new_num = 1
            
            if new_num <= 300:
                self.student_id = f"STU{new_num:03d}"
            else:
                raise ValueError("Maximum student limit reached (STU300)")

class AdmissionForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # School Information
    school_name = db.Column(db.String(200), nullable=False)
    continuous_student_id = db.Column(db.String(50))
    udise_pen = db.Column(db.String(50))
    admission_class = db.Column(db.String(20))
    
    # Personal Information
    birth_register_no = db.Column(db.String(50))
    aadhaar_no = db.Column(db.String(12))
    birth_date = db.Column(db.Date)
    admission_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    
    # Names
    first_name_marathi = db.Column(db.String(100))
    last_name_marathi = db.Column(db.String(100))
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    birth_date_words = db.Column(db.String(200))
    
    # Additional Information
    religion = db.Column(db.String(50))
    caste = db.Column(db.String(50))
    sub_caste = db.Column(db.String(50))
    caste_certificate = db.Column(db.String(100))
    is_minority = db.Column(db.Boolean)
    nationality = db.Column(db.String(50))
    mother_tongue = db.Column(db.String(50))
    mobile_number = db.Column(db.String(15))
    
    # BPL and Disability Status
    bpl_status = db.Column(db.Boolean)
    bpl_number = db.Column(db.String(50))
    disability_status = db.Column(db.Boolean)
    disability_type = db.Column(db.String(100))
    
    # Parent and Address Information
    parent_full_name = db.Column(db.String(200))
    address = db.Column(db.Text)
    
    # File uploads
    student_photo = db.Column(db.String(255))
    parent_photo = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected

class BonafideForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    student_name = db.Column(db.String(200), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    class_standard = db.Column(db.String(20), nullable=False)
    division = db.Column(db.String(10), nullable=False)
    conduct = db.Column(db.String(50), nullable=False)
    caste = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_place = db.Column(db.String(100), nullable=False)
    school_place = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class HostelForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Hostel and Parent Information
    hostel_name = db.Column(db.String(200), nullable=False)
    hostel_address = db.Column(db.String(300))
    parent_name = db.Column(db.String(200), nullable=False)
    parent_address = db.Column(db.Text, nullable=False)
    
    # Student Information
    student_name = db.Column(db.String(200), nullable=False)
    student_address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15))
    caste = db.Column(db.String(100))
    
    # Birth Information
    birth_village = db.Column(db.String(100))
    birth_taluka = db.Column(db.String(100))
    birth_district = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    age_years = db.Column(db.Integer)
    age_months = db.Column(db.Integer)
    
    # Education and Background
    education = db.Column(db.String(200))
    previous_school = db.Column(db.Text)
    annual_income = db.Column(db.String(100))
    exam_results = db.Column(db.Text)
    
    # Guardian Information
    guardian_name = db.Column(db.String(200))
    
    # Administrative
    register_number = db.Column(db.String(50))
    received_date = db.Column(db.Date)
    
    # File uploads
    parent_signature = db.Column(db.String(255))
    student_signature = db.Column(db.String(255))
    warden_signature = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class CaseRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Section 1: Basic Information
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    education = db.Column(db.String(200))
    
    # Father Information
    father_name = db.Column(db.String(200))
    father_education = db.Column(db.String(100))
    father_occupation = db.Column(db.String(100))
    father_income = db.Column(db.String(50))
    
    # Mother Information
    mother_name = db.Column(db.String(200))
    mother_education = db.Column(db.String(100))
    mother_occupation = db.Column(db.String(100))
    mother_income = db.Column(db.String(50))
    
    # Guardian Information
    guardian_name = db.Column(db.String(200))
    guardian_education = db.Column(db.String(100))
    guardian_occupation = db.Column(db.String(100))
    guardian_income = db.Column(db.String(50))
    guardian_address = db.Column(db.Text)
    guardian_mobile = db.Column(db.String(15))
    
    # Address Information
    relatives_address = db.Column(db.Text)
    permanent_address = db.Column(db.Text)
    
    # Social and Cultural Information
    economic_status = db.Column(db.String(50))
    area_type = db.Column(db.String(50))
    religion = db.Column(db.String(50))
    caste = db.Column(db.String(50))
    mother_tongue = db.Column(db.String(50))
    
    # Section 2: Informant Details
    info_relation_personal = db.Column(db.String(200))
    contact_duration = db.Column(db.String(100))
    info_trustworthiness = db.Column(db.String(50))
    info_completeness = db.Column(db.String(50))
    complaint_details = db.Column(db.Text)
    
    # Previous Treatment Information
    past_treatment_medications = db.Column(db.String(50))
    past_treatment_professional = db.Column(db.String(50))
    past_treatment_physical = db.Column(db.String(50))
    past_treatment_other = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class PratinidhanForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    student_name = db.Column(db.String(200), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    class_standard = db.Column(db.String(20), nullable=False)
    division = db.Column(db.String(10), nullable=False)
    conduct = db.Column(db.String(50), nullable=False)
    caste = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_place = db.Column(db.String(100), nullable=False)
    school_place = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
