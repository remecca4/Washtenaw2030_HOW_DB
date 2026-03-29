# Houses of Worship Database Web Application

A full-stack web app for managing and exploring Houses of Worship data, including congregation information, contacts, facilities, solar potential, and climate work.

This system allows organizations to collect, store, edit, and explore data about congregations through an easy-to-use web interface. It also supports CSV bulk imports, user authentication, and cloud image storage for case studies.

The project was designed for Washtenaw county but other groups can adapt the code to build their own HOW databases for research, sustainability programs, or community outreach.

## Features
### Congregation Management

Users can add, edit, and view detailed congregation information including: 

* Name 

* Address 

* Municipal entity

* Denomination

* Contact information

* Website

* Solar Faithful membership status

* Facilities Tracking

Stores building characteristics such as:

* Facility size

* Building age

* Heating, ventilation, and AC systems

* Estimated electric bill

* Sustainability & Climate Data

Tracks sustainability work performed by congregations, including:

* Solar potential

* Climate initiatives

* Building additions

* Environmental impact

### Case Studies

Case study images can be uploaded and displayed for congregations using cloud image hosting.
### Contact Directory

A searchable directory allows filtering congregations by:

* Municipal entity

* Denomination

* Solar Faithful membership status

### CSV Bulk Import

Large datasets can be uploaded via CSV and automatically inserted into the database.

Supported imports include:

* Congregations

* Facilities

* Additions

* Solar potential

* Climate work
The templates to use for these imports are here: https://docs.google.com/spreadsheets/d/13jgp2n4W6qgdXEbd4O1hvG1iYwRxBdnyfIwHcsIU0Mc/edit?usp=sharing \
CSV imports run as background threads so the website remains responsive during large uploads. 

### Authentication System

The site includes a secure login system with: \

 * password hashing

* role-based access control

* admin approval for new users

User roles include: \

* Admin – manage users and database

* User – add and edit congregation data

### Technologies Used

#### Backend

* Python

* Flask

* PostgreSQL

#### Frontend

* HTML

* CSS

* Jinja templates

#### Cloud Services

* Render – web application hosting

* Aiven – managed PostgreSQL database

* Cloudinary – image hosting for case studies

#### System Architecture

The application uses a simple three-layer architecture:

User Browser
     ↓
Flask Web Application
     ↓
PostgreSQL Database
     ↓
Cloudinary (image storage)

The Flask server handles:

authentication

form submissions

database queries

CSV uploads

rendering templates

Project Structure
project/
│
├── app.py
├── db_manager.py
├── parse_csv.py
│
├── templates/
│   ├── home.html
│   ├── forms.html
│   ├── congregations.html
│   ├── contacts.html
│   ├── case_studies.html
│   └── edit_*.html
│
├── static/
│
└── README.md
### Installation
1. Clone the repository
git clone https://github.com/yourusername/how-database.git
cd how-database
2. Install dependencies
pip install -r requirements.txt
3. Set environment variables

The application requires several environment variables. \

SECRET_KEY=your_secret_key \

CLOUDINARY_CLOUD_NAME=your_cloud_name \
CLOUDINARY_API_KEY=your_api_key \
CLOUDINARY_API_SECRET=your_api_secret \

DATABASE_URL=your_postgresql_connection_string \
### Running the Application

Start the Flask server: \

python app.py \

Then open your browser: \

http://localhost:5000 \
### Creating the First Admin

If no admin exists in the database, create one manually by inserting a user with role "admin" in the Users table. \

Admins can: \

approve new users \

reject signup requests \

create new users \

remove users \


### Customizing for Your Own HOW Database

To adapt this system for another organization:

* Update database schema to match your data needs

* Modify CSV parsing logic in parse_csv.py

* Adjust form fields in templates/forms.html

* Update branding and UI

* Deploy your own instance using Render or another hosting platform

Because the database logic is centralized in db_manager.py, most customization can be done without modifying the main application logic.


### Author

Rachel Mecca
Computer Science – University of Michigan