<div align="center">

<img
  src="static/logo.png"
  alt="Houses of Worship Database Web Application"
  width="100%"
/>

# Houses of Worship Database Web Application

**A full-stack web application for managing and exploring Houses of Worship data.**

[Features](#features) •
[Technologies](#technologies-used) •
[Architecture](#system-architecture) •
[Installation](#installation) •
[Usage](#example-usage) •
[Customization](#customizing-for-your-own-how-database) •
[FAQ](#frequently-asked-questions)

</div>

> [!NOTE]
> This project was designed for Washtenaw County, Michigan. Other organizations can adapt the code to create their own Houses of Worship databases for research, sustainability programs, or community outreach.

## Overview

This application allows organizations to collect, store, edit, and explore information about congregations through an easy-to-use web interface.

The system includes:

- Congregation, contact, and facility records
- Solar-potential and climate-work tracking
- Case studies with cloud-hosted images
- A searchable contact directory
- Comma-separated values (CSV) bulk imports
- User authentication and role-based access control

## Table of Contents

- [Features](#features)
  - [Congregation Management](#congregation-management)
  - [Case Studies](#case-studies)
  - [Contact Directory](#contact-directory)
  - [CSV Bulk Import](#csv-bulk-import)
  - [Authentication System](#authentication-system)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Creating the First Admin](#creating-the-first-admin)
- [Example Usage](#example-usage)
  - [Viewing and Editing Congregation Data](#viewing-and-editing-congregation-data)
  - [Adding a New Congregation and Contact](#adding-a-new-congregation-and-contact)
- [Customizing for Your Own HOW Database](#customizing-for-your-own-how-database)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Author](#author)

## Features

### Congregation Management

Users can add, edit, view, and delete detailed congregation information, including:

- Name
- Address
- Municipal entity
- Denomination
- Contact information
- Website
- Solar Faithful membership status

The application stores building characteristics such as:

- Facility size
- Building age
- Heating, ventilation, and air conditioning (HVAC) systems
- Estimated electric bill
- Building additions

It also tracks sustainability initiatives, including:

- Solar potential
- Climate work
- Case studies

### Case Studies

Case studies can be created for congregations. Images can be uploaded and displayed using cloud image hosting.


### Contact Directory

A searchable directory allows users to filter congregations by:

- Municipal entity
- Denomination
- Solar Faithful membership status

### CSV Bulk Import

Large datasets can be uploaded as CSV files and automatically inserted into the database.

Supported imports include:

- Congregations
- Facilities
- Building additions
- Solar potential
- Climate work

View the required formats in the [CSV import templates](https://docs.google.com/spreadsheets/d/13jgp2n4W6qgdXEbd4O1hvG1iYwRxBdnyfIwHcsIU0Mc/edit?usp=sharing).

CSV imports run as background threads so the website remains responsive during large uploads.

### Authentication System

The site includes a secure login system with:

- Password hashing
- Role-based access control
- Administrator approval for new users

#### User Roles

| Role | Permissions |
| --- | --- |
| **Admin** | Manage users, approve registrations, and manage database records |
| **User** | Add and edit congregation data |

## Technologies Used

### Backend

- Python
- Flask
- PostgreSQL

### Frontend

- HTML
- CSS
- Jinja templates

### Cloud Services

- [Render](https://render.com/) — web application hosting
- [Aiven](https://aiven.io/) — PostgreSQL database hosting
- [Cloudinary](https://cloudinary.com/) — image hosting for case studies

## System Architecture
```mermaid
%%{init: {"theme": "base",}}
  "themeVariables": {"fontSize": "24px",}
    "fontFamily": "Arial, sans-serif",
    "lineColor": "#374151"
  },
  "flowchart": {"nodeSpacing": 24,}
    "rankSpacing": 32,
    "curve": "linear",
    "htmlLabels": true
  }
}}%%

flowchart TB
    USER([User / Database Manager])

    subgraph ROUTES["MAIN FLASK ROUTES"]
        direction LR
        AUTH["ACCOUNT<br/>/login · /signup · /logout"]
        VIEW["VIEW<br/>/congregations · /contacts<br/>/case_studies · /filter_congs"]
        FORMS["ADD DATA<br/>/forms · /*/add"]
        EDIT["EDIT / DELETE<br/>/edit_* · /delete_*"]
        ADMIN["ADMIN USERS<br/>/admin/manage-users"]
    end

    subgraph LOGIN_FLOW["LOGIN AND ADMIN FLOW"]
        direction LR
        ENTER["Submit email<br/>and password"]
        LOOKUP["Find user<br/>in users table"]
        PASSWORD{"Password<br/>correct?"}
        APPROVED{"Account<br/>approved?"}
        SESSION["Start session"]
        PROTECTED{"Protected<br/>route?"}
        ROLE{"Admin<br/>role?"}
        DENIED["Return to login"]
    end

    subgraph TABLES["MAIN DATABASE TABLES"]
        direction LR
        USERS[("users")]
        CONG[("congregations")]
        RELATED[("contacts<br/>facilities<br/>additions")]
        PROGRESS[("solar potential<br/>climate work")]
        CASES[("case studies")]
    end

    USER --> AUTH
    USER --> VIEW
    USER --> FORMS
    USER --> EDIT
    USER --> ADMIN

    AUTH --> ENTER
    ENTER --> LOOKUP
    LOOKUP --> USERS
    USERS --> PASSWORD
    PASSWORD -->|No| DENIED
    PASSWORD -->|Yes| APPROVED
    APPROVED -->|No: pending| DENIED
    APPROVED -->|Yes| SESSION

    FORMS --> PROTECTED
    EDIT --> PROTECTED
    ADMIN --> PROTECTED
    PROTECTED -->|Not logged in| DENIED
    PROTECTED -->|Logged in| ROLE
    ROLE -->|Admin route + not admin| DENIED
    ROLE -->|Allowed| FORMS
    ROLE -->|Allowed| EDIT
    ROLE -->|Admin| ADMIN

    VIEW -->|Read| CONG
    VIEW -->|Read| RELATED
    VIEW -->|Read| PROGRESS
    VIEW -->|Read| CASES

    FORMS -->|Insert| CONG
    FORMS -->|Insert| RELATED
    FORMS -->|Insert| PROGRESS
    FORMS -->|Insert| CASES

    EDIT -->|Update / delete| CONG
    EDIT -->|Update / delete| RELATED
    EDIT -->|Update / delete| PROGRESS
    EDIT -->|Delete| CASES

    ADMIN -->|Approve, create,<br/>reject, or remove| USERS

    CONG ---|congregation_id| RELATED
    CONG ---|congregation_id| PROGRESS
    CONG ---|congregation_id| CASES

    classDef person fill:#FFF2B2,stroke:#6B5200,color:#111,stroke-width:3px,font-size:26px;
    classDef route fill:#DCEBFF,stroke:#174F84,color:#111,stroke-width:3px,font-size:24px;
    classDef auth fill:#F3E5F5,stroke:#6A1B9A,color:#111,stroke-width:3px,font-size:24px;
    classDef decision fill:#FFE1A8,stroke:#8A4500,color:#111,stroke-width:3px,font-size:24px;
    classDef denied fill:#FFDADA,stroke:#991B1B,color:#111,stroke-width:3px,font-size:24px;
    classDef table fill:#DDF3E2,stroke:#276738,color:#111,stroke-width:3px,font-size:24px;

    class USER person;
    class AUTH,VIEW,FORMS,EDIT,ADMIN route;
    class ENTER,LOOKUP,SESSION auth;
    class PASSWORD,APPROVED,PROTECTED,ROLE decision;
    class DENIED denied;
    class USERS,CONG,RELATED,PROGRESS,CASES table;
```

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:remecca4/Washtenaw2030_HOW_DB.git
cd Washtenaw2030_HOW_DB
```


### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

#### macOS or Linux

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file or configure the following variables in your deployment environment:

```dotenv
SECRET_KEY=your_secret_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
DATABASE_URL=your_postgresql_connection_string
```

## Running the Application

Start the Flask server:

```bash
python app.py
```

Then open the application in your browser:

```text
http://localhost:5000
```

## Creating the First Admin

If no administrator exists in the database, manually insert a user with the role `admin` into the `Users` table.

Administrators can:

- Approve new users
- Reject signup requests
- Create new users
- Remove users
- Manage database records

> [!IMPORTANT]
> Store only a properly hashed password. Do not insert a plain-text password into the database.

## Example Usage

### Viewing Congregation Data

<p align="center">
  <img
    src="docs/view_cong.gif"
    alt="Demonstration of viewing congregation data"
    width="850"
  />
</p>

### Editing Congregation Data

<p align="center">
  <img
    src="docs/edit_cong.gif"
    alt="Demonstration of editing congregation data"
    width="850"
  />
</p>

### Adding a New Congregation


<p align="center">
  <img
    src="docs/add_datap1.gif"
    alt="Demonstration of adding a new congregation"
    width="850"
  />
</p>

### Adding a New Contact

<p align="center">
  <img
    src="docs/add_datap2.gif"
    alt="Demonstration of adding a new contact"
    width="850"
  />
</p>

## Customizing for Your Own HOW Database

To adapt this system for another organization:

1. Update the database schema to match your data requirements.
2. Modify the CSV parsing logic in `parse_csv.py`.
3. Adjust form fields in `templates/forms.html`.
4. Adjust the congregation view in `templates/congregations.html`.
5. Update the branding and user interface.
6. Deploy your instance using Render or another hosting platform.

Because the database logic is centralized in `db_manager.py`, most customization can be completed without modifying the main application logic.

## Frequently Asked Questions

### Can I add multiple administrators to the website?

Yes. You can add as many administrators as needed.

### Do I have to use Aiven and Render to deploy the application?

No. You can use any compatible deployment method and PostgreSQL hosting provider.

### Can I change data after entering it through the website?

Yes. Authorized users can edit or delete data entered through the website.

## Author

**Rachel Mecca**

Computer Science  
University of Michigan