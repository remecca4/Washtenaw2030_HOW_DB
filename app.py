from datetime import datetime as datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for,Blueprint, flash, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from db_manager import DatabaseManager
from werkzeug.utils import secure_filename
from parse_csv import parse_insert_additions_csv,parse_insert_climate_work_csv,parse_insert_congregation_csv,parse_insert_facilities_csv,parse_insert_solar_csv
from flask_bcrypt import Bcrypt


import os
app = Flask(__name__)
db = DatabaseManager()
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key") 

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

#user stuff
class User(UserMixin):
    def __init__(self, row):
        self.id = row[0]
        self.email = row[1]
        self.password_hash = row[2]
        self.role = row[3]
        self.congregation_id = row[4]
        self.approved = row[5] 

@login_manager.user_loader
def load_user(user_id):
   row = db.get_user_by_id(user_id)
   return User(row) if row else None



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email)
        user_id=db.get_user_id(email)
        print(user_id)
        row = db.get_user_by_id(user_id)
        print(row)
        #print(row[2])
        if row and bcrypt.check_password_hash(row[2], password):
         

         if row[5] == 0:
          flash("Your account is awaiting admin approval.")
          return redirect("/login")
         login_user(User(row))
         return redirect("/")
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        print(password_hash)
        # Create user as pending
        db.insert_user(
            email=email,
            password_hash=password_hash,
            role="user",
            congregation_id=None,
            approved=0  # pending
        )

        flash("Signup request submitted. Awaiting admin approval.")
        return redirect("/login")

    return render_template("signup.html")



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_exists():
    row = db.fetchone("SELECT 1 FROM Users WHERE role = 'admin'")
    return row is not None



@app.route("/admin/manage-users/approve/<email>")
@login_required
@admin_required
def approve_user(email):
    
    user_id=db.get_user_id(email)
    db.approve_user(user_id)
    flash(f"{email} approved!")
    return redirect("/admin//manage-users")

@app.route("/admin/manage-users/reject/<email>")
@login_required
@admin_required
def reject_user(email):
    user_id=db.get_user_id(email)
    db.delete_User(user_id)
    flash(f"{email} rejected.")
    return redirect("/admin/manage-users")

def bootstrap():
    if admin_exists():
        return "Admin already exists", 403

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        db.insert_user(email=email, password_hash=password_hash, role="admin",congregation_id=None)
        flash("Admin registered!")
        return redirect("/login")

    return render_template("bootstrap.html")


@app.route("/admin/manage-users")
@login_required
@admin_required
def manage_users():
    users = db.fetchall("SELECT email FROM Users WHERE approved = 0 AND role = 'user'")
    print("PENDING USERS:", users)
    return render_template("manage_users.html", users=users)
@app.route("/admin/manage-users/create-user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        db.insert_user(email=email, password_hash=password_hash, role=role,congregation_id=None)

        flash("User registered!")
        return redirect("/")

    return render_template("manage_users.html")
@app.route("/admin/manage-users/remove-user", methods=["GET", "POST"])
@login_required
@admin_required
def remove_user():
    if request.method == "POST":
        email = request.form["email"]
        print("email")
        user_id=db.get_user_id(email)
        db.delete_User(user_id)

        return redirect("/")

    return render_template("manage_users.html")
# Home page
@app.route("/")
def home():
    return render_template("home.html")

# Combined forms page
@app.route("/forms", methods=["GET"])
def view_forms():
    congregations = db.get_all_congregations()
    return render_template(
        "forms.html",
        congregations=congregations,
        upload_congregations_url=url_for("upload_congregations_csv")  # add this
    )

# Add congregation

@app.route("/congregation/add", methods=["POST"])
@login_required
def congregation_form():
    name = request.form.get("name")
    address = request.form.get("address")
    municipal_entity = request.form.get("municipal_entity")
    denomination = request.form.get("denomination")
    size = request.form.get("size")
    size = int(size) if size and size.isdigit() else None
    email = request.form.get("email")
    phone_number = request.form.get("phone_number")
    website = request.form.get("website") or None

    db.insert_congregation(name, address, municipal_entity, denomination, size, email, phone_number, website)
    return redirect(url_for("view_forms"))

# Add facility
@app.route("/facility/add", methods=["POST"])
@login_required
def facilities_form():
    congregation_id = int(request.form["congregation_id"])  # selected from dropdown
    facility_size = request.form.get("facility_size")
    facility_size = int(facility_size) if facility_size and facility_size.isdigit() else None
    age = request.form.get("age")
    age = int(age) if age and age.isdigit() else None
    heating_sys = request.form.get("heating_sys")
    vent_sys = request.form.get("vent_sys")
    ac_sys = request.form.get("ac_sys")

    db.insert_facility(congregation_id, facility_size, age, heating_sys, vent_sys, ac_sys)
    return redirect(url_for("view_forms"))

# Add addition
@app.route("/addition/add", methods=["POST"])
@login_required
def additions_form():
    congregation_id = int(request.form["congregation_id"])  # selected from dropdown
    addition_size = request.form.get("addition_size")
    addition_size = int(addition_size) if addition_size and addition_size.isdigit() else None
    addition_date_raw = request.form.get("addition_date")
    addition_date = datetime.strptime(addition_date_raw, "%Y-%m-%d").date()
    db.insert_addition(congregation_id, addition_size,addition_date)
    return redirect(url_for("view_forms"))

# Add solar potential
@app.route("/solar/add", methods=["POST"])
@login_required
def solar_form():
    congregation_id = int(request.form["congregation_id"])
    usable_sunlight = request.form.get("usable_sunlight")
    usable_sunlight = int(usable_sunlight) if usable_sunlight and usable_sunlight.isdigit() else None
    solar_panel_space=request.form.get("solar_panel_space")
    solar_panel_space = int(solar_panel_space) if solar_panel_space and solar_panel_space.isdigit() else None
    savings=request.form.get("savings")
    savings=int(savings) if savings and savings.isdigit() else None
    co2_savings=request.form.get("co2_savings")
    co2_savings=int(co2_savings) if co2_savings and co2_savings.isdigit() else None
    db.insert_solar_potential(congregation_id,usable_sunlight,solar_panel_space,savings,co2_savings)
    return redirect(url_for("view_forms"))

@app.route("/climate_work/add", methods=["POST"])
@login_required
def climate_work_form():
    congregation_id = int(request.form["congregation_id"])
    work_type=request.form.get("work_type")
    start_date_raw = request.form.get("start_date")
    start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
    end_date_raw = request.form.get("end_date")
    end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
    description=request.form.get("description")
    impact=request.form.get("impact")
    db.insert_climate_work(congregation_id,work_type,start_date,end_date,description,impact)
    return redirect(url_for("view_forms"))

# View congregations page
@app.route("/congregations", methods=["GET"])
def view_congregations():
    congregations = db.get_all_congregations()
    selected_id = request.args.get("id", type=int) # from dropdown selection
    print(selected_id)
    selected_congregation = None
    facilities = []
    additions = []
    solar = []
    climate_work = []

    if selected_id:
        # Get detailed info from DB
        selected_congregation = db.get_congregation_by_id(selected_id)
        print(selected_congregation)
        facilities = db.get_facilities_by_congregation(selected_id)
        additions = db.get_additions_by_congregation(selected_id)
        solar = db.get_solar_by_congregation(selected_id)
        climate_work = db.get_climate_work_by_congregation(selected_id)

    return render_template(
        "congregations.html",
        congregations=congregations,
        selected_congregation=selected_congregation,
        facilities=facilities,
        additions=additions,
        solar=solar,
        climate_work=climate_work,
    )

@app.route("/edit_congregation/<int:cong_id>", methods=["GET", "POST"])
@login_required
def edit_congregation(cong_id):
    if request.method == "POST":
        data = {
            "name": db.get_congregation_by_id(cong_id)["name"],
            "address": request.form["address"],
            "municipal_entity": request.form["municipal_entity"],
            "denomination": request.form["denomination"],
            "size": request.form["size"],
            "email": request.form["email"],
            "phone_number": request.form["phone_number"],
            "website": request.form["website"],
        }
        db.update_congregation(cong_id, data)
        return redirect(f"/congregations?id={cong_id}")

    congregation = db.get_congregation_by_id(cong_id)
    return render_template("edit_congregation.html", congregation=congregation)

@app.route("/delete_congregation/<int:cong_id>", methods=["POST"])
@login_required
def delete_congregation(cong_id):
    db.delete_congregation(cong_id)
    return redirect("/congregations")

@app.route("/edit_facility/<int:facility_id>", methods=["GET", "POST"])
@login_required
def edit_facility(facility_id):
    facility = db.get_facility_by_id(facility_id)
    congregation_name = db.get_congregation_by_id(facility["congregation_id"])['name']
    print(congregation_name)
    if request.method == "POST":
        data={
          "facility_size": request.form["facility_size"],
            "age": request.form["age"],
            "heating_sys": request.form["heating_sys"],
            "vent_sys": request.form["vent_sys"],
            "ac_sys": request.form["ac_sys"],
            "est_electric_bill": request.form["est_electric_bill"]
        }
        db.update_facility(facility_id,data)
        return redirect(f"/congregations?id={facility['congregation_id']}")

    return render_template("edit_facility.html",
                           facility=facility,
                           congregation_name=congregation_name)

@app.route("/delete_facility/<int:facility_id>", methods=["POST"])
@login_required
def delete_facility(facility_id):
    db.delete_facility(facility_id)
    return redirect("/congregations")

@app.route("/edit_addition/<int:addition_id>", methods=["GET", "POST"])
@login_required
def edit_addition(addition_id):
    addition = db.get_addition_by_id(addition_id)
    congregation_name = db.get_congregation_by_id(addition["congregation_id"])['name']
    
    if request.method == "POST":
        data={
          "addition_size": request.form["addition_size"],
            "addition_date": request.form["addition_date"]
           
        }
        db.update_addition(
            addition_id,
            data
        )
        return redirect(f"/congregations?id={addition['congregation_id']}")

    return render_template("edit_addition.html",
                           addition=addition,
                           congregation_name=congregation_name)

@app.route("/delete_addition/<int:addition_id>", methods=["POST"])
@login_required
def delete_addition(addition_id):
    db.delete_addition(addition_id)
    return redirect("/congregations")

@app.route("/edit_solar/<int:solar_pot_id>", methods=["GET", "POST"])
@login_required
def edit_solar(solar_pot_id):
    solar_pot = db.get_solar_by_id(solar_pot_id)
    congregation_name = db.get_congregation_by_id(solar_pot["congregation_id"])['name']
   
    if request.method == "POST":
        data={
          "usable_sunlight": request.form["usable_sunlight"],
            "solar_panel_space": request.form["solar_panel_space"],
            "savings": request.form["savings"],
            "co2_savings": request.form["co2_savings"]
           
        }
        db.update_solar(solar_pot_id,data )
        return redirect(f"/congregations?id={solar_pot['congregation_id']}")

    return render_template("edit_solar_pot.html",
                           solar_pot=solar_pot,
                           congregation_name=congregation_name)


@app.route("/delete_solar/<int:solar_pot_id>", methods=["POST"])
@login_required
def delete_solar(solar_pot_id):
    db.delete_Solar_Potential(solar_pot_id)
    return redirect("/congregations")

@app.route("/edit_climate_work/<int:climate_work_id>", methods=["GET", "POST"])
@login_required
def edit_climate_work(climate_work_id):
    climate_work = db.get_climate_work_by_id(climate_work_id)
    congregation_name = db.get_congregation_by_id(climate_work["congregation_id"])['name']
   
    if request.method == "POST":
        data={
          "work_type": request.form["work_type"],
            "start_date": request.form["start_date"],
            "end_date": request.form["end_date"],
            "description": request.form["description"],
            "impact": request.form["impact"]
           
        }
        db.update_climate_work(
            climate_work_id,
            data
        )
        return redirect(f"/congregations?id={climate_work['congregation_id']}")

    return render_template("edit_climate_work.html",
                           climate_work=climate_work,
                           congregation_name=congregation_name)

@app.route("/delete_climate_work/<int:climate_work_id>", methods=["POST"])
@login_required
def delete_climate_work(climate_work_id):
    db.delete_Climate_Work(climate_work_id)
    return redirect("/congregations")




UPLOAD_FOLDER = "/tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/congregations")
@login_required
def upload_congregations_csv():
    file = request.files.get("csv_file")
    if not file:
        flash("No file uploaded.")
        return redirect(request.referrer)

    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)

    parse_insert_congregation_csv(path)

    flash("Congregations CSV imported!")
    return redirect(request.referrer)


@app.route("/upload/facilities")
@login_required
def upload_facilities_csv():
    file = request.files.get("csv_file")
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    parse_insert_facilities_csv(path)
    flash("Facilities CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/additions")
@login_required
def upload_additions_csv():
    file = request.files.get("csv_file")
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    parse_insert_additions_csv(path)
    flash("Additions CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/solar")
@login_required

def upload_solar_csv():
    file = request.files.get("csv_file")
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    parse_insert_solar_csv(path)
    flash("Solar potential CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/climate_work")
@login_required
def upload_climate_work_csv():
    file = request.files.get("csv_file")
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    parse_insert_climate_work_csv(path)
    flash("Climate Work CSV imported!")
    return redirect(request.referrer)
if __name__ == "__main__":
    app.run(debug=True)