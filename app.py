from flask import Flask, render_template, request, redirect, session, url_for,send_from_directory
import pymysql
import os

app = Flask(__name__)
app.secret_key = "petfinder_secret_key"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        'uploads',
        filename
    )

# ---------------- DATABASE CONNECTION ----------------

db = pymysql.connect(
    host="localhost",
    user="root",
    password="root123*",
    database="petfinder"
)

# ---------------- HOME ----------------

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = db.cursor()

        sql = """
        INSERT INTO users
        (name,email,password)
        VALUES(%s,%s,%s)
        """

        cursor.execute(
            sql,
            (name, email, password)
        )

        db.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        cursor = db.cursor()

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        cursor.execute(
            sql,
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            session['name'] = user[1]

            return redirect(url_for('dashboard'))

        return "Invalid Email or Password"

    return render_template('login.html')

# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if 'name' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor()

    cursor.execute("""
    SELECT *
    FROM pet_reports
    ORDER BY created_at DESC
    LIMIT 3
    """)

    reports = cursor.fetchall()

    return render_template(
    'dashboard.html',
    reports=reports
)

# ---------------- UPLOAD PET REPORT ----------------

@app.route('/upload', methods=['POST'])
def upload():

    if 'name' not in session:
        return redirect(url_for('login'))

    pet_name = request.form.get('pet_name')
    pet_type = request.form.get('pet_type')
    status = request.form.get('status')
    location = request.form.get('location')
    contact = request.form.get('contact')
    description = request.form.get('description')

    photo = request.files['pet_photo']

    filename = photo.filename

    photo.save(
        os.path.join('uploads', filename)
    )

    cursor = db.cursor()

    sql = """
    INSERT INTO pet_reports
    (
        pet_name,
        pet_type,
        status,
        location,
        contact,
        description,
        photo_name
    )
    VALUES(%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(
        sql,
        (
            pet_name,
            pet_type,
            status,
            location,
            contact,
            description,
            filename
        )
    )

    db.commit()

    print("Pet Report Saved Successfully")

    return redirect(url_for('dashboard'))

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))

# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)