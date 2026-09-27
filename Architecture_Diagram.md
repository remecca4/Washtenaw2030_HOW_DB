 ```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontSize": "24px",
    "fontFamily": "Arial",
    "lineColor": "#374151"
  },
  "flowchart": {
    "nodeSpacing": 25,
    "rankSpacing": 35,
    "curve": "linear",
    "htmlLabels": true
  }
}}%%

flowchart TB
    USER([User / Database Manager])

    subgraph ROUTES["MAIN FLASK ROUTES"]
        direction LR
        AUTH["LOGIN<br/>/login · /signup · /logout"]
        VIEW["VIEW<br/>/congregations · /contacts<br/>/case_studies · /filter_congs"]
        FORMS["ADD DATA<br/>/forms · /*/add"]
        EDIT["EDIT / DELETE<br/>/edit_* · /delete_*"]
        ADMIN["USERS<br/>/admin/manage-users"]
    end

    subgraph LOGIN["LOGIN FLOW"]
        direction LR
        ENTER["Enter email<br/>and password"]
        VALID{"Valid and<br/>approved?"}
        SESSION["Start session"]
        DENIED["Login denied"]
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
    ENTER --> USERS
    USERS --> VALID
    VALID -->|Yes| SESSION
    VALID -->|No| DENIED

    FORMS -->|Login required| SESSION
    EDIT -->|Login required| SESSION
    ADMIN -->|Login + admin required| SESSION

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

    ADMIN -->|Manage| USERS

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
    class ENTER,SESSION auth;
    class VALID decision;
    class DENIED denied;
    class USERS,CONG,RELATED,PROGRESS,CASES table;
```