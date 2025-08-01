import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func

from app import app, db
from models import User, AdmissionForm, BonafideForm, HostelForm, CaseRecord, PratinidhanForm
from forms import LoginForm, RegistrationForm, AdmissionFormForm, BonafideFormForm

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard') if not current_user.is_admin else url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('admin_dashboard') if user.is_admin else url_for('student_dashboard')
            flash('प्रवेश यशस्वी झाला! / Login successful!', 'success')
            return redirect(next_page)
        flash('चुकीचे वापरकर्ता नाव किंवा पासवर्ड / Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | 
                                        (User.email == form.email.data)).first()
        if existing_user:
            flash('वापरकर्ता नाव किंवा ईमेल आधीपासून अस्तित्वात आहे / Username or email already exists', 'danger')
            return render_template('register.html', form=form)
        
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.set_password(form.password.data)
        
        try:
            user.generate_student_id()
            db.session.add(user)
            db.session.commit()
            flash(f'नोंदणी यशस्वी झाली! तुमचा विद्यार्थी ID: {user.student_id} / Registration successful! Your Student ID: {user.student_id}', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('तुम्ही यशस्वीरित्या लॉग आउट झाला आहात / You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get statistics for current user
    stats = {
        'admission_forms': AdmissionForm.query.filter_by(user_id=current_user.id).count(),
        'bonafide_forms': BonafideForm.query.filter_by(user_id=current_user.id).count(),
        'hostel_forms': HostelForm.query.filter_by(user_id=current_user.id).count(),
        'case_records': CaseRecord.query.filter_by(user_id=current_user.id).count(),
        'pratinidhan_forms': PratinidhanForm.query.filter_by(user_id=current_user.id).count(),
    }
    
    # Get recent forms
    recent_forms = []
    for form_class in [AdmissionForm, BonafideForm, HostelForm, CaseRecord, PratinidhanForm]:
        forms = form_class.query.filter_by(user_id=current_user.id).order_by(form_class.created_at.desc()).limit(5).all()
        for form in forms:
            recent_forms.append({
                'type': form_class.__name__,
                'id': form.id,
                'created_at': form.created_at,
                'status': form.status
            })
    
    recent_forms.sort(key=lambda x: x['created_at'], reverse=True)
    recent_forms = recent_forms[:10]
    
    return render_template('student_dashboard.html', stats=stats, recent_forms=recent_forms)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('प्रवेश नाकारला / Access denied', 'danger')
        return redirect(url_for('student_dashboard'))
    
    # Get overall statistics
    stats = {
        'total_students': User.query.filter_by(is_admin=False).count(),
        'total_admission_forms': AdmissionForm.query.count(),
        'total_bonafide_forms': BonafideForm.query.count(),
        'total_hostel_forms': HostelForm.query.count(),
        'total_case_records': CaseRecord.query.count(),
        'total_pratinidhan_forms': PratinidhanForm.query.count(),
        'pending_forms': (
            AdmissionForm.query.filter_by(status='pending').count() +
            BonafideForm.query.filter_by(status='pending').count() +
            HostelForm.query.filter_by(status='pending').count() +
            CaseRecord.query.filter_by(status='pending').count() +
            PratinidhanForm.query.filter_by(status='pending').count()
        )
    }
    
    # Get recent forms from all users
    recent_forms = []
    for form_class in [AdmissionForm, BonafideForm, HostelForm, CaseRecord, PratinidhanForm]:
        forms = form_class.query.order_by(form_class.created_at.desc()).limit(10).all()
        for form in forms:
            user = User.query.get(form.user_id)
            if user:
                recent_forms.append({
                    'type': form_class.__name__,
                    'id': form.id,
                    'created_at': form.created_at,
                    'status': form.status,
                    'student_name': user.full_name,
                    'student_id': user.student_id
                })
    
    recent_forms.sort(key=lambda x: x['created_at'], reverse=True)
    recent_forms = recent_forms[:20]
    
    return render_template('admin_dashboard.html', stats=stats, recent_forms=recent_forms)

@app.route('/admission_form', methods=['GET', 'POST'])
@login_required
def admission_form():
    form = AdmissionFormForm()
    
    if form.validate_on_submit():
        # Handle file uploads
        student_photo_filename = None
        parent_photo_filename = None
        
        if form.student_photo.data:
            student_photo_filename = save_file(form.student_photo.data)
        
        if form.parent_photo.data:
            parent_photo_filename = save_file(form.parent_photo.data)
        
        admission_form = AdmissionForm()
        admission_form.user_id = current_user.id
        admission_form.school_name = form.school_name.data
        admission_form.continuous_student_id = form.continuous_student_id.data
        admission_form.udise_pen = form.udise_pen.data
        admission_form.admission_class = form.admission_class.data
        admission_form.birth_register_no = form.birth_register_no.data
        admission_form.aadhaar_no = form.aadhaar_no.data
        admission_form.birth_date = form.birth_date.data
        admission_form.admission_date = form.admission_date.data
        admission_form.gender = form.gender.data
        admission_form.student_photo = student_photo_filename
        admission_form.parent_photo = parent_photo_filename
        admission_form.first_name_marathi = form.first_name_marathi.data
        admission_form.last_name_marathi = form.last_name_marathi.data
        admission_form.father_name = form.father_name.data
        admission_form.mother_name = form.mother_name.data
        admission_form.birth_date_words = form.birth_date_words.data
        admission_form.religion = form.religion.data
        admission_form.caste = form.caste.data
        admission_form.sub_caste = form.sub_caste.data
        admission_form.caste_certificate = form.caste_certificate.data
        admission_form.is_minority = form.is_minority.data
        admission_form.nationality = form.nationality.data
        admission_form.mother_tongue = form.mother_tongue.data
        admission_form.mobile_number = form.mobile_number.data
        admission_form.bpl_status = form.bpl_status.data
        admission_form.bpl_number = form.bpl_number.data
        admission_form.disability_status = form.disability_status.data
        admission_form.disability_type = form.disability_type.data
        admission_form.parent_full_name = form.parent_full_name.data
        admission_form.address = form.address.data
        
        db.session.add(admission_form)
        db.session.commit()
        
        flash('प्रवेश अर्ज यशस्वीरित्या जमा झाला! / Admission form submitted successfully!', 'success')
        return redirect(url_for('form_success', form_type='admission', form_id=admission_form.id))
    
    return render_template('admission_form.html', form=form)

@app.route('/bonafide_form', methods=['GET', 'POST'])
@login_required
def bonafide_form():
    form = BonafideFormForm()
    
    if form.validate_on_submit():
        bonafide = BonafideForm()
        bonafide.user_id = current_user.id
        bonafide.student_name = form.student_name.data
        bonafide.academic_year = form.academic_year.data
        bonafide.class_standard = form.class_standard.data
        bonafide.division = form.division.data
        bonafide.conduct = form.conduct.data
        bonafide.caste = form.caste.data
        bonafide.birth_date = form.birth_date.data
        bonafide.birth_place = form.birth_place.data
        bonafide.school_place = form.school_place.data
        
        db.session.add(bonafide)
        db.session.commit()
        
        flash('बोनाफाइड अर्ज यशस्वीरित्या जमा झाला! / Bonafide form submitted successfully!', 'success')
        return redirect(url_for('form_success', form_type='bonafide', form_id=bonafide.id))
    
    return render_template('bonafide_form.html', form=form)

@app.route('/bonafide_certificate/<int:form_id>')
@login_required
def bonafide_certificate(form_id):
    bonafide = BonafideForm.query.get_or_404(form_id)
    
    # Check if user owns this form or is admin
    if bonafide.user_id != current_user.id and not current_user.is_admin:
        flash('प्रवेश नाकारला / Access denied', 'danger')
        return redirect(url_for('student_dashboard'))
    
    return render_template('bonafide_certificate.html', bonafide=bonafide, student=bonafide.student)

@app.route('/hostel_form', methods=['GET', 'POST'])
@login_required
def hostel_form():
    if request.method == 'POST':
        # Handle file uploads
        parent_signature = save_file(request.files.get('parent_signature'))
        student_signature = save_file(request.files.get('student_signature'))
        warden_signature = save_file(request.files.get('warden_signature'))
        
        hostel = HostelForm()
        hostel.user_id = current_user.id
        hostel.hostel_name = request.form.get('hostel_name')
        hostel.hostel_address = request.form.get('hostel_address')
        hostel.parent_name = request.form.get('parent_name')
        hostel.parent_address = request.form.get('parent_address')
        hostel.student_name = request.form.get('student_name')
        hostel.student_address = request.form.get('student_address')
        hostel.phone = request.form.get('phone')
        hostel.caste = request.form.get('caste')
        hostel.birth_village = request.form.get('birth_village')
        hostel.birth_taluka = request.form.get('birth_taluka')
        hostel.birth_district = request.form.get('birth_district')
        hostel.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
        hostel.age_years = int(request.form.get('age_years')) if request.form.get('age_years') else None
        hostel.age_months = int(request.form.get('age_months')) if request.form.get('age_months') else None
        hostel.education = request.form.get('education')
        hostel.previous_school = request.form.get('previous_school')
        hostel.annual_income = request.form.get('annual_income')
        hostel.exam_results = request.form.get('exam_results')
        hostel.guardian_name = request.form.get('guardian_name')
        hostel.register_number = request.form.get('register_number')
        hostel.received_date = datetime.strptime(request.form.get('received_date'), '%Y-%m-%d').date() if request.form.get('received_date') else None
        hostel.parent_signature = parent_signature
        hostel.student_signature = student_signature
        hostel.warden_signature = warden_signature
        
        db.session.add(hostel)
        db.session.commit()
        
        flash('वसतिगृह अर्ज यशस्वीरित्या जमा झाला! / Hostel form submitted successfully!', 'success')
        return redirect(url_for('form_success', form_type='hostel', form_id=hostel.id))
    
    return render_template('hostel_form.html')

@app.route('/case_record_form', methods=['GET', 'POST'])
@login_required
def case_record_form():
    if request.method == 'POST':
        case_record = CaseRecord()
        case_record.user_id = current_user.id
        case_record.name = request.form.get('name')
        case_record.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
        case_record.age = int(request.form.get('age')) if request.form.get('age') else None
        case_record.gender = request.form.get('gender')
        case_record.education = request.form.get('education')
        case_record.father_name = request.form.get('father_name')
        case_record.father_education = request.form.get('father_education')
        case_record.father_occupation = request.form.get('father_occupation')
        case_record.father_income = request.form.get('father_income')
        case_record.mother_name = request.form.get('mother_name')
        case_record.mother_education = request.form.get('mother_education')
        case_record.mother_occupation = request.form.get('mother_occupation')
        case_record.mother_income = request.form.get('mother_income')
        case_record.guardian_name = request.form.get('guardian_name')
        case_record.guardian_education = request.form.get('guardian_education')
        case_record.guardian_occupation = request.form.get('guardian_occupation')
        case_record.guardian_income = request.form.get('guardian_income')
        case_record.guardian_address = request.form.get('guardian_address')
        case_record.guardian_mobile = request.form.get('guardian_mobile')
        case_record.relatives_address = request.form.get('relatives_address')
        case_record.permanent_address = request.form.get('permanent_address')
        case_record.economic_status = request.form.get('economic_status')
        case_record.area_type = request.form.get('area_type')
        case_record.religion = request.form.get('religion')
        case_record.caste = request.form.get('caste')
        case_record.mother_tongue = request.form.get('mother_tongue')
        case_record.info_relation_personal = request.form.get('info_relation_personal')
        case_record.contact_duration = request.form.get('contact_duration')
        case_record.info_trustworthiness = request.form.get('info_trustworthiness')
        case_record.info_completeness = request.form.get('info_completeness')
        case_record.complaint_details = request.form.get('complaint_details')
        case_record.past_treatment_medications = request.form.get('past_treatment_medications')
        case_record.past_treatment_professional = request.form.get('past_treatment_professional')
        case_record.past_treatment_physical = request.form.get('past_treatment_physical')
        case_record.past_treatment_other = request.form.get('past_treatment_other')
        
        db.session.add(case_record)
        db.session.commit()
        
        flash('केस रेकॉर्ड यशस्वीरित्या जमा झाला! / Case record submitted successfully!', 'success')
        return redirect(url_for('form_success', form_type='case_record', form_id=case_record.id))
    
    return render_template('case_record_form.html')

@app.route('/pratinidhan_form', methods=['GET', 'POST'])
@login_required
def pratinidhan_form():
    if request.method == 'POST':
        pratinidhan = PratinidhanForm()
        pratinidhan.user_id = current_user.id
        pratinidhan.student_name = request.form.get('student_name')
        pratinidhan.academic_year = request.form.get('academic_year')
        pratinidhan.class_standard = request.form.get('class_standard')
        pratinidhan.division = request.form.get('division')
        pratinidhan.conduct = request.form.get('conduct')
        pratinidhan.caste = request.form.get('caste')
        pratinidhan.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
        pratinidhan.birth_place = request.form.get('birth_place')
        pratinidhan.school_place = request.form.get('school_place')
        
        db.session.add(pratinidhan)
        db.session.commit()
        
        flash('प्रतिनिधान अर्ज यशस्वीरित्या जमा झाला! / Pratinidhan form submitted successfully!', 'success')
        return redirect(url_for('form_success', form_type='pratinidhan', form_id=pratinidhan.id))
    
    return render_template('pratinidhan_form.html')

@app.route('/form_success/<form_type>/<int:form_id>')
@login_required
def form_success(form_type, form_id):
    form_names = {
        'admission': 'प्रवेश अर्ज / Admission Form',
        'bonafide': 'बोनाफाइड प्रमाणपत्र / Bonafide Certificate',
        'hostel': 'वसतिगृह अर्ज / Hostel Application',
        'case_record': 'केस रेकॉर्ड / Case Record',
        'pratinidhan': 'प्रतिनिधान प्रमाणपत्र / Pratinidhan Certificate'
    }
    
    return render_template('form_success.html', 
                         form_type=form_type, 
                         form_id=form_id, 
                         form_name=form_names.get(form_type, 'Form'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Admin routes for managing forms
@app.route('/admin/forms/<form_type>')
@login_required
def admin_forms(form_type):
    if not current_user.is_admin:
        flash('प्रवेश नाकारला / Access denied', 'danger')
        return redirect(url_for('student_dashboard'))
    
    form_models = {
        'admission': AdmissionForm,
        'bonafide': BonafideForm,
        'hostel': HostelForm,
        'case_record': CaseRecord,
        'pratinidhan': PratinidhanForm
    }
    
    if form_type not in form_models:
        flash('अवैध फॉर्म प्रकार / Invalid form type', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    forms = form_models[form_type].query.order_by(form_models[form_type].created_at.desc()).all()
    
    # Add student information to each form
    for form in forms:
        form.student = User.query.get(form.user_id)
    
    return render_template('admin_forms.html', forms=forms, form_type=form_type)

@app.route('/admin/form/<form_type>/<int:form_id>/update_status', methods=['POST'])
@login_required
def update_form_status(form_type, form_id):
    if not current_user.is_admin:
        flash('प्रवेश नाकारला / Access denied', 'danger')
        return redirect(url_for('student_dashboard'))
    
    form_models = {
        'admission': AdmissionForm,
        'bonafide': BonafideForm,
        'hostel': HostelForm,
        'case_record': CaseRecord,
        'pratinidhan': PratinidhanForm
    }
    
    if form_type not in form_models:
        flash('अवैध फॉर्म प्रकार / Invalid form type', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    form = form_models[form_type].query.get_or_404(form_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'approved', 'rejected']:
        form.status = new_status
        db.session.commit()
        flash('स्थिती अद्यतनित केली गेली / Status updated', 'success')
    else:
        flash('अवैध स्थिती / Invalid status', 'danger')
    
    return redirect(url_for('admin_forms', form_type=form_type))
