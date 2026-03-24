from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print("Login Data:")
        print("Email:", email)
        print("Password:", password)

        return "Login form submitted successfully!"

    return render_template('login.html')


@app.route('/student-register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        roll_number = request.form.get('roll_number')
        branch = request.form.get('branch')
        year = request.form.get('year')
        cgpa = request.form.get('cgpa')
        phone = request.form.get('phone')
        skills = request.form.get('skills')
        resume_link = request.form.get('resume_link')

        print("Student Registration Data:")
        print(full_name, email, password, confirm_password, roll_number, branch, year, cgpa, phone, skills, resume_link)

        return "Student registration submitted successfully!"

    return render_template('student_registration.html')


@app.route('/company-register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        hr_name = request.form.get('hr_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        website = request.form.get('website')
        industry_type = request.form.get('industry_type')
        location = request.form.get('location')
        description = request.form.get('description')

        print("Company Registration Data:")
        print(company_name, hr_name, email, password, confirm_password, phone, website, industry_type, location, description)

        return "Company registration submitted successfully!"

    return render_template('company_registration.html')


if __name__ == '__main__':
    app.run(debug=True)