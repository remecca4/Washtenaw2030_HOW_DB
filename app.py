from datetime import datetime as datetime
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from db_manager import DatabaseManager
from werkzeug.utils import secure_filename
from parse_csv import parse_insert_additions_csv,parse_insert_climate_work_csv,parse_insert_congregation_csv,parse_insert_facilities_csv,parse_insert_solar_csv,parse_insert_contacts_csv



import os
import cloudinary
import cloudinary.uploader


app = Flask(__name__)
print(__name__)

db = DatabaseManager()
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key") 
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, row):
        '''
        Summary
        ---------------------------------------------------------------------
        User Class Constructor
       
        Parameters
        ---------------------------------------------------------------------
        :param  row: list, row in the users table with the following elements:
         :param user_id, email, passsword hash, role, congregation_id, approved status
        '''
        self.id = row[0]
        self.email = row[1]
        self.password_hash = row[2]
        self.role = row[3]
        self.congregation_id = row[4]
        self.approved = row[5] 

@login_manager.user_loader
def load_user(user_id):
   '''
   Summary
   ----------------------------------------------------
   Gets user row from database  and makes a User Object 
   using the user's id 
   
   Parameters
   -----------------------------------------------------
   :param user_id: int, id of user to return
  
   Returns
   -----------------------------------------------------
   User Object
   '''
   row = db.get_user_by_id(user_id)
   return User(row) if row else None

@app.route("/login", methods=["GET", "POST"])
def login():
    '''
    Summary
    -------------------------------------------------------------------
    Called when someone tries to log in. Redirects user to home page if 
    a login is successful. Returns to login page if login is unsuccesful
   
    Returns
    --------------------------------------------------------------------
    Render template if unsuccessful login
    Redirect Response Object if login is succssful
    '''
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email)
        user_id=db.get_user_id(email)
        print(user_id)
        row = db.get_user_by_id(user_id)
        print(row)
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
    '''
    -------------------------------------------------------------------
    Summary
    -------------------------------------------------------------------
    Called when a user logs out. Logs user out and redirects user to login page.
  
    Returns
    --------------------------------------------------------------------
    Redirect Response Object to login page
    '''
    logout_user()
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    '''
    Summary
    ----------------------------------------------------------
    Creates a new user with a pending approval status

    Returns
    --------------------------------------------------------------------
    Redirect Response Object to login page
    '''
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
            approved=False  # pending
        )

        flash("Signup request submitted. Awaiting admin approval.")
        return redirect("/login")

    return render_template("signup.html")

def admin_required(f):
    '''
   Function that hides parts of the website for non-admin users
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_exists():
    '''
   Summary
   ------------------------------------------------------------
   Checks if a user with an admin role exisits in the database
   
   Returns
   ------------------------------------------------------------
   User row if admin exists or None if no admin exists.
    '''
    row = db.fetchone("SELECT 1 FROM Users WHERE role = 'admin'")
    return row is not None

@app.route("/admin/manage-users/approve/<email>")
@login_required
@admin_required
def approve_user(email):
    '''
    Summary
    -------------------------------------------
    Approves a user with `email` as their email
    
    Parameters
    ---------------------------------------------
    :param email: str, email of user to approve

    Returns
    ---------------------------------------------
    Redirect Response Object to manage users page
    '''
    user_id=db.get_user_id(email)
    db.approve_user(user_id)
    flash(f"{email} approved!")
    return redirect("/admin//manage-users")

@app.route("/admin/manage-users/reject/<email>")
@login_required
@admin_required
def reject_user(email):
    '''
    Summary
    -------------------------------------------
    Rejects and  a user with `email` as their email 
    by removing them from the database
    
    Parameters
    ---------------------------------------------
    :param email: str, email of user to reject

    Returns
    ---------------------------------------------
    Redirect Response Object to manage users page
    '''
    user_id=db.get_user_id(email)
    db.delete_User(user_id)
    flash(f"{email} rejected.")
    return redirect("/admin/manage-users")


@app.route("/admin/manage-users")
@login_required
@admin_required
def manage_users():
    '''
    Summary
    -----------------------------------
    Selects all pending users to approve

    Returns
    -------------------------------------
    Render template to manage_users.html

    '''
    users = db.fetchall("SELECT email FROM Users WHERE approved = FALSE AND role = 'user'")
    print("PENDING USERS:", users)
    return render_template("manage_users.html", users=users)

@app.route("/admin/manage-users/create-user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    '''
    Summary
    ------------------------------------------------------
    Inserts a user into the database using data recieved 
    from the create user website form.
    
    Returns
    ------------------------------------------------------
    Redirect Response Object to home page

    '''
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        db.insert_user(email=email, password_hash=password_hash, role=role,congregation_id=None,approved=True)

        flash("User registered!")
        return redirect("/")

    return render_template("manage_users.html")

@app.route("/admin/manage-users/remove-user", methods=["GET", "POST"])
@login_required
@admin_required
def remove_user():
    '''
    Summary
    ------------------------------------------------------
    Removes a user from the database using data recieved 
    from the remove user website form.
    
    Returns
    ------------------------------------------------------
    Render template to manage users page

    '''
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
    '''
    Returns render template to home page
    '''
    return render_template("home.html")


@app.route("/forms", methods=["GET"])
def view_forms():
    '''
    Summary
    ------------------------------------------
     Displays the combined forms page

    Returns
    -----------------------------------------
    Render Template to forms.html 
    with all congregations for the dropdowns
    '''
    congregations = db.get_all_congregations()
    return render_template(
        "forms.html",
        congregations=congregations,
        upload_congregations_url=url_for("upload_congregations_csv"),
        upload_contacts_url=url_for("upload_contacts_csv"),      
        upload_facilities_url=url_for("upload_facilities_csv"),
        upload_additions_url=url_for("upload_additions_csv"),      
        upload_solar_url=url_for("upload_solar_csv"),
        upload_climate_work_url=url_for("upload_climate_work_csv")
    )


@app.route("/congregation/add", methods=["POST"])
@login_required
def congregation_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from congregation form and inserts it 
    into the congregation table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
    name = request.form.get("name")
    address = request.form.get("address")
    municipal_entity = request.form.get("municipal_entity")
    denomination = request.form.get("denomination")
    size = request.form.get("size")
    size = int(size) if size and size.isdigit() else None
    website = request.form.get("website") or None
    sf_member_status=request.form.get("sf_member_status") or None
    db.insert_congregation(name, address, municipal_entity, denomination, size, website,sf_member_status)
    return redirect(url_for("view_forms"))

@app.route("/contact/add", methods=["POST"])
@login_required
def contacts_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from contacts form and inserts it 
    into the contacts table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
    congregation_id = int(request.form["congregation_id"])  
    name = request.form.get("name")
    role = request.form.get("role")
    email = request.form.get("email")
    phone_number = request.form.get("phone_number")
    print("tis the db's prob")
    db.insert_contact(congregation_id, name,role,email,phone_number)
    return redirect(url_for("view_forms"))

@app.route("/facility/add", methods=["POST"])
@login_required
def facilities_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from facilities form and inserts it 
    into the facilities table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
    congregation_id = int(request.form["congregation_id"])  
    facility_size = request.form.get("facility_size")
    facility_size = int(facility_size) if facility_size and facility_size.isdigit() else None
    year_built = request.form.get("year_built")
    year_built = int(year_built) if year_built and year_built.isdigit() else None
    heating_sys = request.form.get("heating_sys")
    vent_sys = request.form.get("vent_sys")
    ac_sys = request.form.get("ac_sys")
    electric_bill=request.form.get("electric_bill") 
    electric_bill = int(electric_bill) if electric_bill and electric_bill.isdigit() else None
    db.insert_facility(congregation_id, facility_size,year_built, heating_sys, vent_sys, ac_sys,electric_bill)
    return redirect(url_for("view_forms"))


@app.route("/addition/add", methods=["POST"])
@login_required
def additions_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from addition form and inserts it 
    into the additions table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
    congregation_id = int(request.form["congregation_id"])  # selected from dropdown
    addition_size = request.form.get("addition_size")
    addition_size = int(addition_size) if addition_size and addition_size.isdigit() else None
    addition_date_raw = request.form.get("addition_date")
    addition_date = datetime.strptime(addition_date_raw, "%Y-%m-%d").date()
    db.insert_addition(congregation_id, addition_size,addition_date)
    return redirect(url_for("view_forms"))

@app.route("/solar/add", methods=["POST"])
@login_required
def solar_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from solar form and inserts it 
    into the csolar potential table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
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
    '''
    Summary
    -----------------------------------------------
    Gets data from climate work form and inserts it 
    into the climate work table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
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

@app.route("/case_study/add", methods=["POST"])
@login_required
def case_study_form():
    '''
    Summary
    -----------------------------------------------
    Gets data from climate work form and inserts it 
    into the climate work table in the database

    Returns
    ----------------------------------------------
    Redirect Response Object to view forms 

    '''
    congregation_id = int(request.form["congregation_id"])
    
    
    file = request.files.get("case_study_image")

    if not file or file.filename == "":
     flash("No case study uploaded.")
     return redirect(request.referrer)

# Upload to Cloudinary
    result = cloudinary.uploader.upload(file)

# The secure URL you store in DB
    image_url = result["secure_url"]

    db.insert_case_study(congregation_id, image_url)

    flash("Case study uploaded!")
    return redirect(url_for("view_forms"))
    
@app.route("/congregations", methods=["GET"])
def view_congregations():
    '''
    Summary
    -------------------------------------
    Displays all information about the 
    congregation selected from the dropdown menu
    
    Returns
    ------------------------------------------
    Render Template to forms.html 
    with all congregations for the dropdowns 
    and selected congregation to display
    '''
    congregations = db.get_all_congregations()
    selected_id = request.args.get("id", type=int) # from dropdown selection
    selected_congregation = None
    contacts=[]
    facilities = []
    additions = []
    solar = []
    climate_work = []

    if selected_id:
        # Get detailed info from DB
        selected_congregation = db.get_congregation_by_id(selected_id)
        print(selected_congregation)
        contacts=db.get_contacts_by_congregation(selected_id)
        facilities = db.get_facilities_by_congregation(selected_id)
        additions = db.get_additions_by_congregation(selected_id)
        solar = db.get_solar_by_congregation(selected_id)
        climate_work = db.get_climate_work_by_congregation(selected_id)

    return render_template(
        "congregations.html",
        congregations=congregations,
        selected_congregation=selected_congregation,
        contacts=contacts,
        facilities=facilities,
        additions=additions,
        solar=solar,
        climate_work=climate_work,
    )

@app.route("/edit_congregation/<int:cong_id>", methods=["GET", "POST"])
@login_required
def edit_congregation(cong_id):
    '''
    Summary
    ------------------------------------------------
    Edits congregation with id `cong_id` in database 
    with data provided by website form
    
    Parameters
    -------------------------------------------------
     :param cong_id: int, id of congregation to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page for 
    the congreagtion with id=`cong_id`
    '''
    if request.method == "POST":
        data = {
            "name": db.get_congregation_by_id(cong_id)["name"],
            "address": request.form["address"],
            "municipal_entity": request.form["municipal_entity"],
            "denomination": request.form["denomination"],
            "size": request.form["size"],
            "website": request.form["website"],
            "sf_member_status":request.form["sf_member_status"]
        }
        db.update_congregation(cong_id, data)
        return redirect(f"/congregations?id={cong_id}")

    congregation = db.get_congregation_by_id(cong_id)
    return render_template("edit_congregation.html", congregation=congregation)

@app.route("/delete_congregation/<int:cong_id>", methods=["POST"])
@login_required
def delete_congregation(cong_id):
    '''
    Summary
    ------------------------------------------------
    Deletes congregation with id `cong_id` from database 
    
    Parameters
    -------------------------------------------------
     :param cong_id: int, id of congregation to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
    db.delete_congregation(cong_id)
    return redirect(f"/congregations?id={cong_id}")

@app.route("/edit_contact/<int:contact_id>", methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    '''
    Summary
    ------------------------------------------------
    Edits contact with id `contact_id` in database 
    with data provided by website form
    
    Parameters
    -------------------------------------------------
     :param contact_id: int, id of contact to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page for 
    the congregation corresponding to the contact
    '''
    contact = db.get_contact_by_id(contact_id)
    congregation_name = db.get_congregation_by_id(contact["congregation_id"])['name']
    print(congregation_name)
    if request.method == "POST":
        data={
          "name": request.form["name"],
            "role": request.form["role"],
            "email": request.form["email"],
            "phone_number": request.form["phone_number"]
        }
        db.update_contact(contact_id,data)
        return redirect(f"/congregations?id={contact['congregation_id']}")

    return render_template("edit_contact.html",
                           contact=contact,
                           congregation_name=congregation_name)

@app.route("/delete_contact/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact(contact_id):
    '''
    Summary
    ------------------------------------------------
    Deletes contact with id `contact_id` from database 
    
    Parameters
    -------------------------------------------------
     :param contact_id: int, id of contact to delete

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
    contact=db.get_contact_by_id(contact_id)
    db.delete_contact(contact_id)
    return redirect(f"/congregations?id={contact['congregation_id']}")

@app.route("/edit_facility/<int:facility_id>", methods=["GET", "POST"])
@login_required
def edit_facility(facility_id):
    '''
    Summary
    ------------------------------------------------
    Edits facility with id `facility_id` in database 
    with data provided by website form
    
    Parameters
    -------------------------------------------------
     :param facility_id: int, id of facility to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page for 
    the congregation corresponding to the facility
    '''
    facility = db.get_facility_by_id(facility_id)
    congregation_name = db.get_congregation_by_id(facility["congregation_id"])['name']
    print(congregation_name)
    if request.method == "POST":
        data={
          "facility_size": request.form["facility_size"],
            "year_built": request.form["year_built"],
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
    '''
    Summary
    ------------------------------------------------
    Deletes facility with id `facility_id` from database 
    
    Parameters
    -------------------------------------------------
     :param facility_id: int, id of facility to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
    facility=db.get_facility_by_id(facility_id)
    db.delete_facility(facility_id)
    return redirect(f"/congregations?id={facility['congregation_id']}")

@app.route("/edit_addition/<int:addition_id>", methods=["GET", "POST"])
@login_required
def edit_addition(addition_id):
    '''
    Summary
    ------------------------------------------------
    Deletes addition with id `addition_id` from database 
    
    Parameters
    -------------------------------------------------
     :param addition_id: int, id of addition to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
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
    addition=db.get_addition_by_id(addition_id)
    db.delete_addition(addition_id)
    return redirect(f"/congregations?id={addition['congregation_id']}")

@app.route("/edit_solar/<int:solar_pot_id>", methods=["GET", "POST"])
@login_required
def edit_solar(solar_pot_id):
    '''
    Summary
    ------------------------------------------------
    Edits solar potential with id `solar_pot_id` in database 
    with data provided by website form
    
    Parameters
    -------------------------------------------------
     :param solar_pot_id: int, id of solar potential to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page for 
    the congregation corresponding to the solar potential
    '''
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
    '''
    Summary
    ------------------------------------------------
    Deletes solar potential with id `solar_pot_id` from database 
    
    Parameters
    -------------------------------------------------
     :param solar_pot_id: int, id of solar potential to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
    solar_pot=db.get_solar_by_id(solar_pot_id)
    db.delete_Solar_Potential(solar_pot_id)
    return redirect(f"/congregations?id={solar_pot['congregation_id']}")

@app.route("/edit_climate_work/<int:climate_work_id>", methods=["GET", "POST"])
@login_required
def edit_climate_work(climate_work_id):
    '''
    Summary
    ------------------------------------------------
    Edits climate work with id `climate_work_id` in database 
    with data provided by website form
    
    Parameters
    -------------------------------------------------
     :param climate_work_id: int, id of climate work to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page for 
    the congregation corresponding to the climate work
    '''
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
    '''
    Summary
    ------------------------------------------------
    Deletes climate work with id `climate_work_id` from database 
    
    Parameters
    -------------------------------------------------
     :param climate_work_id: int, id of solar potential to edit

    Returns
    ---------------------------------------------------
    Redirect Response Object to view congregation page 
    '''
    climate_work=db.get_climate_work_by_id(climate_work_id)
    db.delete_Climate_Work(climate_work_id)
    return redirect(f"/congregations?id={climate_work['congregation_id']}")
@app.route("/delete_case_study/<int:case_study_id>", methods=["POST"])
@login_required
def delete_case_study(case_study_id):
    '''
    Summary
    ------------------------------------------------
    Deletes case study with id `congregation_id` from database 
    
    Parameters
    -------------------------------------------------
     :param case_study_id: int, id of case study to delete

    Returns
    ---------------------------------------------------
    Redirect Response Object to case studies page 
    '''
    db.delete_case_study(case_study_id)
    return redirect("/case_studies")
UPLOAD_FOLDER = "/tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/congregations")
@login_required
def upload_congregations_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the congregations table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work OUTSIDE the request
    threading.Thread(
        target=parse_insert_congregation_csv,
        args=(path),
        daemon=True
    ).start()

    flash("Congregations CSV Imported!.")
    return redirect(request.referrer)

@app.post("/upload/contacts")
@login_required
def upload_contacts_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the contacts table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work outside the request
    threading.Thread(
        target=parse_insert_contacts_csv,
        args=(path,),
        daemon=True
    ).start()
    
    flash("Contacts CSV imported!")
    return redirect(request.referrer)
@app.post("/upload/facilities")
@login_required
def upload_facilities_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the facilities table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work OUTSIDE the request
    threading.Thread(
        target=parse_insert_facilities_csv,
        args=(path,),
        daemon=True
    ).start()
    
    flash("Facilities CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/additions")
@login_required
def upload_additions_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the additions table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work OUTSIDE the request
    threading.Thread(
        target=parse_insert_additions_csv,
        args=(path,),
        daemon=True
    ).start()
    
    flash("Additions CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/solar")
@login_required
def upload_solar_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the solar potential table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work OUTSIDE the request
    threading.Thread(
        target=parse_insert_solar_csv,
        args=(path,),
        daemon=True
    ).start()
    
    flash("Solar potential CSV imported!")
    return redirect(request.referrer)

@app.post("/upload/climate_work")
@login_required
def upload_climate_work_csv():
    '''
    Summary
    ------------------------------------------------
    Uploads data formated in a csv to the climate work table

    Returns
    ---------------------------------------------------
    Redirect Response Object to add data page
    '''
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file uploaded.")
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    # Run heavy work OUTSIDE the request
    threading.Thread(
        target=parse_insert_climate_work_csv,
        args=(path,),
        daemon=True
    ).start()
    flash("Climate Work CSV imported!")
    return redirect(request.referrer)

@app.route("/filter_congs")
def filter_congs():
    '''
    Summary
    ------------------------------------------------
    Displays HOW contacts filtered by municipal entity,
    denomination, and sf_status

    Returns
    ---------------------------------------------------
    Render Template to filter_congs.html 
    '''
    municipal = request.args.get("municipal", "")
    denomination = request.args.get("denomination", "")
    sf_status = request.args.get("sf_status", "")
    search_query = request.args.get("search", "").strip()
    # Base query
    query = "SELECT congregation_id, name, municipal_entity, denomination, sf_member_status FROM congregations"
    conditions = []
    params = []

    # Add filters
    if municipal:
        conditions.append("municipal_entity = %s")
        params.append(municipal)
    if denomination:
        conditions.append("denomination = %s")
        params.append(denomination)
    if sf_status:
      conditions.append("sf_member_status = %s")
      params.append(sf_status)
    if search_query:
      conditions.append( "name ILIKE %s")
      params.append(f"%{search_query}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
   
    query += " ORDER BY name"

    # Fetch HOWs
    congregations = db.fetchall(query, params)

    # Fetch distinct options for filters
    municipal_options = [row[0] for row in db.fetchall("SELECT DISTINCT municipal_entity FROM congregations ORDER BY municipal_entity")]
    denomination_options = [row[0] for row in db.fetchall("SELECT DISTINCT denomination FROM congregations ORDER BY denomination")]
    sf_options = [row[0] for row in db.fetchall("SELECT DISTINCT sf_member_status FROM congregations ORDER BY sf_member_status")]
    return render_template(
        "filter_congs.html",
        hows=congregations,
        municipal_options=municipal_options,
        denomination_options=denomination_options,
        sf_options=sf_options,
        selected_municipal=municipal,
        selected_denomination=denomination,
        selected_sf_status=sf_status,
        search_query=search_query
    )
@app.route("/contacts")
def how_contacts():
    municipal = request.args.get("municipal", "")
    denomination = request.args.get("denomination", "")
    sf_status = request.args.get("sf_status", "")
    contact_name = request.args.get("contact_name", "")
    cong_name= request.args.get("cong_name", "")

    query = """
        SELECT 
            c.name,
            g.municipal_entity,
            g.denomination,
            c.email,
            c.phone_number,
            g.sf_member_status,
            c.role,
            g.name
        FROM contacts c
        JOIN congregations g ON c.congregation_id = g.congregation_id
    """

    conditions = []
    params = []

    if municipal:
        conditions.append("g.municipal_entity = %s")
        params.append(municipal)

    if denomination:
        conditions.append("g.denomination = %s")
        params.append(denomination)

    if sf_status:
        conditions.append("g.sf_member_status = %s")
        params.append(sf_status)

    if contact_name:
        conditions.append("c.name ILIKE %s")
        params.append(f"%{contact_name}%")
    if cong_name:
        conditions.append("g.name ILIKE %s")
        params.append(f"%{cong_name}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY g.name"

    contacts = db.fetchall(query, params)

    municipal_options = [row[0] for row in db.fetchall(
        "SELECT DISTINCT municipal_entity FROM congregations ORDER BY municipal_entity"
    )]

    denomination_options = [row[0] for row in db.fetchall(
        "SELECT DISTINCT denomination FROM congregations ORDER BY denomination"
    )]

    sf_options = [row[0] for row in db.fetchall(
        "SELECT DISTINCT sf_member_status FROM congregations ORDER BY sf_member_status"
    )]

    return render_template(
        "contacts.html",
        contacts=contacts,
        municipal_options=municipal_options,
        denomination_options=denomination_options,
        sf_options=sf_options,
        selected_municipal=municipal,
        selected_denomination=denomination,
        selected_sf_status=sf_status,
        contact_name=contact_name,
        cong_name=cong_name
    )
@app.route("/case_studies")
def how_case_studies():
    '''
    Summary
    ------------------------------------------------
    Displays case studies for the selected congregation

    Returns
    ---------------------------------------------------
    Render Template to case_studies.html 
    '''
    cong_ids = db.get_all_case_study_cong_ids()
    selected_id = request.args.get("id", type=int) # from dropdown selection
    case_studies=[]
    selected_congregation=None
    if selected_id:
        # Get detailed info from DB
        case_studies=db.get_case_study_by_cong_id(selected_id)
        print(case_studies)
        selected_congregation=db.get_congregation_by_id(selected_id)
    return render_template(
        "case_studies.html",
        congregations=cong_ids,
        selected_congregation=selected_congregation,
        case_studies=case_studies,
    )
if __name__ == "__main__":
    app.run(debug=True)