from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "abc123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    skills = db.Column(db.String(300))
    resume_filename = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    applications = db.relationship("Application", backref="student", lazy=True, cascade="all, delete-orphan")

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    hr_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    website = db.Column(db.String(200))
    industry_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    jobs = db.relationship("Job", backref="company", lazy=True, cascade="all, delete-orphan")

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    required_skills = db.Column(db.String(300))
    experience = db.Column(db.String(50))
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="Active")
    applications = db.relationship("Application", backref="job", lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    status = db.Column(db.String(20), default="Applied") 
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        if role == "student":
            student = Student.query.filter_by(email=email, password=password).first()
            if student and student.is_active:
                session.clear()
                session["student_id"] = student.id
                session["role"] = "student"
                return redirect(url_for("student_dashboard"))
            else:
                flash("Invalid or inactive student")
                return redirect(url_for("login"))

        elif role == "company":
            company = Company.query.filter_by(email=email, password=password).first()
            if company and company.is_active:
                if company.approved:
                    session.clear()
                    session["company_id"] = company.id
                    session["role"] = "company"
                    return redirect(url_for("company_dashboard"))
                else:
                    flash("Company not approved by admin yet")
                    return redirect(url_for("login"))
            else:
                flash("Invalid or inactive company")
                return redirect(url_for("login"))

        elif role == "admin":
            if email == "admin@gmail.com" and password == "admin123":
                session.clear()
                session["role"] = "admin"
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid admin credentials")
                return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        roll_number = request.form["roll_number"]
        branch = request.form["branch"]
        year = int(request.form["year"])
        cgpa = float(request.form["cgpa"])
        phone = request.form["phone"]
        skills = request.form.get("skills")
        resume = request.files.get("resume")

        if password != confirm_password:
            flash("Password not match")
            return redirect(url_for("student_register"))

        existing_student = Student.query.filter(
            (Student.email == email) | (Student.roll_number == roll_number)
        ).first()

        if existing_student:
            flash("Student already registered")
            return redirect(url_for("student_register"))

        resume_filename = None
        if resume and resume.filename:
            resume_filename = secure_filename(resume.filename)
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))

        student = Student(
            full_name=full_name,
            email=email,
            password=password,
            roll_number=roll_number,
            branch=branch,
            year=year,
            cgpa=cgpa,
            phone=phone,
            skills=skills,
            resume_filename=resume_filename
        )

        db.session.add(student)
        db.session.commit()
        flash("Student registered successfully")
        return redirect(url_for("login"))

    return render_template("student_register.html")

@app.route("/company_register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        company_name = request.form["company_name"]
        hr_name = request.form["hr_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        phone = request.form["phone"]
        website = request.form.get("website")
        industry_type = request.form["industry_type"]
        location = request.form["location"]
        description = request.form.get("description")

        if password != confirm_password:
            flash("Password not match")
            return redirect(url_for("company_register"))

        existing_company = Company.query.filter_by(email=email).first()
        if existing_company:
            flash("Company already registered")
            return redirect(url_for("company_register"))

        company = Company(
            company_name=company_name,
            hr_name=hr_name,
            email=email,
            password=password,
            phone=phone,
            website=website,
            industry_type=industry_type,
            location=location,
            description=description,
            approved=False
        )

        db.session.add(company)
        db.session.commit()
        flash("Company registered successfully. Wait for admin approval.")
        return redirect(url_for("login"))

    return render_template("company_register.html")

@app.route("/student_dashboard")
def student_dashboard():
    if session.get("role") != "student":
        flash("Please login as student")
        return redirect(url_for("login"))

    student = Student.query.get(session.get("student_id"))
    if not student:
        flash("Student not found")
        return redirect(url_for("login"))

    jobs = Job.query.filter_by(approved=True, status="Active").all()
    applications = Application.query.filter_by(student_id=student.id).all()
    applied_job_ids = [application.job_id for application in applications]

    return render_template(
        "student_dashboard.html",
        student=student,
        jobs=jobs,
        applications=applications,
        applied_job_ids=applied_job_ids
    )

@app.route("/company_dashboard")
def company_dashboard():
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    company = Company.query.get(session.get("company_id"))
    if not company:
        flash("Company not found")
        return redirect(url_for("login"))

    jobs = company.jobs

    applicants_data = []
    for job in jobs:
        for application in job.applications:
            if application.student:
                applicants_data.append({
                "application_id": application.id,
                "job_title": job.title,
                "student_name": application.student.full_name,
                "student_email": application.student.email,
                "branch": application.student.branch,
                "cgpa": application.student.cgpa,
                "skills": application.student.skills,
                "resume_filename": application.student.resume_filename,
                "status": application.status
            })

    return render_template(
        "company_dashboard.html",
        company=company,
        jobs=jobs,
        applicants_data=applicants_data
    )

@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Please login as admin")
        return redirect(url_for("login"))

    companies = Company.query.all()
    students = Student.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    return render_template(
        "admin_dashboard.html",
        companies=companies,
        students=students,
        jobs=jobs,
        applications=applications,
        total_students=len(students),
        total_companies=len(companies),
        total_jobs=len(jobs),
        total_applications=len(applications)
    )

@app.route("/approve_company/<int:company_id>")
def approve_company(company_id):
    if session.get("role") != "admin":
        flash("Only admin can approve companies")
        return redirect(url_for("login"))

    company = Company.query.get_or_404(company_id)
    company.approved = True
    db.session.commit()
    flash("Company approved successfully")
    return redirect(url_for("admin_dashboard"))


@app.route("/approve_job/<int:job_id>")
def approve_job(job_id):
    if session.get("role") != "admin":
        flash("Only admin can approve jobs")
        return redirect(url_for("login"))

    job = Job.query.get_or_404(job_id)
    job.approved = True
    job.status = "Active"
    db.session.commit()
    flash("Job approved successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/deactivate_student/<int:id>")
def deactivate_student(id):
    if session.get("role") != "admin":
        flash("Only admin can perform this action")
        return redirect(url_for("login"))

    student = Student.query.get_or_404(id)
    student.is_active = False
    db.session.commit()
    flash("Student deactivated successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/deactivate_company/<int:id>")
def deactivate_company(id):
    if session.get("role") != "admin":
        flash("Only admin can perform this action")
        return redirect(url_for("login"))

    company = Company.query.get_or_404(id)
    company.is_active = False
    db.session.commit()
    flash("Company deactivated successfully")
    return redirect(url_for("admin_dashboard"))

@app.route("/search")
def search():
    query = request.args.get("query")

    students = Student.query.filter(
        Student.full_name.ilike(f"%{query}%") |
        Student.roll_number.ilike(f"%{query}%") |
        Student.email.ilike(f"%{query}%") |
        Student.phone.ilike(f"%{query}%")
    ).all()

    companies = Company.query.filter(
        Company.company_name.ilike(f"%{query}%") |
        Company.industry_type.ilike(f"%{query}%")
    ).all()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        jobs=Job.query.all(),
        applications=Application.query.all(),
        total_students=len(students),
        total_companies=len(companies),
        total_jobs=len(Job.query.all()),
        total_applications=len(Application.query.all())
    )

@app.route("/post_job", methods=["POST"])
def post_job():
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    company = Company.query.get(session.get("company_id"))
    if not company:
        flash("Company not found")
        return redirect(url_for("login"))

    title = request.form["title"]
    role = request.form["role_name"]
    package = request.form["package"]
    required_skills = request.form.get("required_skills")
    experience = request.form.get("experience")
    eligibility_cgpa = float(request.form["eligibility_cgpa"])
    location = request.form["location"]
    description = request.form["description"]

    job = Job(
        title=title,
        role=role,
        package=package,
        required_skills=required_skills,
        experience=experience,
        eligibility_cgpa=eligibility_cgpa,
        location=location,
        description=description,
        company_id=company.id,
        approved=False,
        status="Pending"
    )

    db.session.add(job)
    db.session.commit()
    flash("Job posted successfully. Waiting for admin approval.")
    return redirect(url_for("company_dashboard"))

@app.route("/apply_job/<int:job_id>")
def apply_job(job_id):
    if session.get("role") != "student":
        flash("Please login as student")
        return redirect(url_for("login"))

    student = Student.query.get(session.get("student_id"))
    job = Job.query.get_or_404(job_id)

    if not student:
        flash("Student not found")
        return redirect(url_for("login"))

    if not job.approved or job.status != "Active":
        flash("This job is not available for application")
        return redirect(url_for("student_dashboard"))

    existing_application = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing_application:
        flash("You have already applied for this job")
        return redirect(url_for("student_dashboard"))

    if student.cgpa < job.eligibility_cgpa:
        flash("You are not eligible for this job based on CGPA")
        return redirect(url_for("student_dashboard"))

    application = Application(student_id=student.id, job_id=job.id)
    db.session.add(application)
    db.session.commit()
    flash("Applied successfully")
    return redirect(url_for("student_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for("login"))

@app.route("/view_applicants/<int:job_id>")
def view_applicants(job_id):
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    job = Job.query.get_or_404(job_id)

    if job.company_id != session.get("company_id"):
        flash("Unauthorized access")
        return redirect(url_for("company_dashboard"))

    applications = Application.query.filter_by(job_id=job_id).all()

    applicants = []
    for application in applications:
        student = Student.query.get(application.student_id)
        if student:
            applicants.append({
                "application_id": application.id,
                "full_name": student.full_name,
                "email": student.email,
                "branch": student.branch,
                "cgpa": student.cgpa,
                "skills": student.skills,
                "resume_filename": student.resume_filename,
                "status": application.status  
            })

    return render_template("view_applicants.html", job=job, applicants=applicants)

@app.route("/update_job_status/<int:job_id>/<string:new_status>")
def update_job_status(job_id, new_status):
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    job = Job.query.get_or_404(job_id)
    if job.company_id != session.get("company_id"):
        flash("You cannot update this job")
        return redirect(url_for("company_dashboard"))

    if new_status not in ["Active", "Closed"]:
        flash("Invalid status")
        return redirect(url_for("company_dashboard"))

    job.status = new_status
    db.session.commit()
    flash(f"Job status updated to {new_status}")
    return redirect(url_for("company_dashboard"))

@app.route("/shortlist/<int:application_id>")
def shortlist(application_id):
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    application = Application.query.get_or_404(application_id)
    job = Job.query.get(application.job_id)

    if job.company_id != session.get("company_id"):
        flash("You cannot update this application")
        return redirect(url_for("company_dashboard"))

    application.status = "Shortlisted"
    db.session.commit()
    flash("Application shortlisted")
    return redirect(url_for("view_applicants", job_id=job.id))

@app.route("/select/<int:application_id>")
def select_application(application_id):
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    application = Application.query.get_or_404(application_id)
    job = Job.query.get(application.job_id)

    if job.company_id != session.get("company_id"):
        flash("You cannot update this application")
        return redirect(url_for("company_dashboard"))

    application.status = "Selected"
    db.session.commit()
    flash("Application selected")
    return redirect(url_for("view_applicants", job_id=job.id))

@app.route("/reject/<int:application_id>")
def reject(application_id):
    if session.get("role") != "company":
        flash("Please login as company")
        return redirect(url_for("login"))

    application = Application.query.get_or_404(application_id)
    job = Job.query.get(application.job_id)

    if job.company_id != session.get("company_id"):
        flash("You cannot update this application")
        return redirect(url_for("company_dashboard"))

    application.status = "Rejected"
    db.session.commit()
    flash("Application rejected")
    return redirect(url_for("view_applicants", job_id=job.id))

if __name__ == "__main__":
    app.run(debug=True)