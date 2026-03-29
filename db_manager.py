import re

import psycopg2
import os


class DatabaseManager:
    def __init__(self):
        '''
         Database Manager Constructor
         -------------------------------------
         Parameters
         ------------------------------------
         db_path: string, path to database
        '''
        
        self._setup_database()
        
    def _setup_database(self):
        '''
         Database Manager Constructor
         -------------------------------------
         executes script to set up HOW database
        '''
        schema_script = """
    
        """
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cong_table_script="""
        -- Table to store basic info about houses of worship
        CREATE TABLE IF NOT EXISTS congregations (
        congregation_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        municipal_entity TEXT, -- eg. Ann Arbor, Chelsea, etc.
        denomination TEXT,
        size INTEGER DEFAULT 0,  -- amount of people in the HOW
        website TEXT,
        sf_member_status TEXT CHECK (sf_member_status IN ('Unknown', 'Unsure', 'Interested', 'Not Interested','Member'))
       );"""
        cursor.execute(cong_table_script)
        cong_table_script="""
        -- Table to store basic info about houses of worship
        CREATE TABLE IF NOT EXISTS contacts (
        contact_id SERIAL PRIMARY KEY,
        congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        role TEXT,
        email TEXT,  
        phone_number TEXT
       );"""
        cursor.execute(cong_table_script)
        facility_table_script="""
         -- Table to keep track of facility info
         CREATE TABLE IF NOT EXISTS  facilities  (
         facility_id SERIAL PRIMARY KEY,
         congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
         facility_size INTEGER, --size of the facility (sq ft.)
         year_built INTEGER, --year the building was built
         heating_sys TEXT, --heating system type
         vent_sys  TEXT, --ventilation system type
         ac_sys TEXT,  --ac system type
         est_electric_bill DOUBLE PRECISION  --estimated electric bill   
          );"""
        cursor.execute(facility_table_script)
        additions_table_script="""
         -- Table to track any additions to facilities
         CREATE TABLE IF NOT EXISTS additions (
         addition_id SERIAL PRIMARY KEY,
         congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
         addition_size INTEGER, --size of the addition (sq ft.)
         addition_date TIMESTAMP --date addition was added 
         );
          """
        cursor.execute(additions_table_script)
        solar_table_script="""-- Table to record each congregation's solar potential
         CREATE TABLE IF NOT EXISTS solar_potential (
        solar_pot_id SERIAL PRIMARY KEY,
        congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
        usable_sunlight INTEGER, --est amount of usable sunlight per year in hours
        solar_panel_space INTEGER, --amount of space for solar panels (sq ft.)
        savings INTEGER, --estimated amount of monetary savings per year from installing solar panels(dollars)
        co2_savings INTEGER --estimated CO2 savings per year from installing solar panels(metric tons) 
        );"""
        cursor.execute(solar_table_script)
        climate_table_script="""
          -- Tracks any climate work each congregation has done
         CREATE TABLE IF NOT EXISTS climate_work(
        climate_work_id SERIAL PRIMARY KEY,
        congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
        work_type TEXT NOT NULL, --category of climate work
        start_date TIMESTAMP, --start date of work
       end_date TIMESTAMP, --end date of work (leave blank if still ongoing)
       description  TEXT, --description of work
       impact TEXT  --add any impacts here 
       );"""
        cursor.execute(climate_table_script)
        users_table_script="""
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
        congregation_id INTEGER REFERENCES congregations(congregation_id) ON DELETE CASCADE,
        approved BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
        cursor.execute(users_table_script)
        conn.commit()
        
        case_study_table_script="""
           CREATE TABLE IF NOT EXISTS case_studies (
             case_study_id SERIAL PRIMARY KEY,
             congregation_id INTEGER NOT NULL REFERENCES congregations(congregation_id) ON DELETE CASCADE,
             case_study_path TEXT
            );
         """
        cursor.execute(case_study_table_script)
        conn.commit()
    def clear_tables(self):
        '''
        clears all tables in database
        '''
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cursor.execute("DELETE FROM congregations;")
        conn.commit()
        print("CLEAR TABLES")
        conn.close()

    def insert_congregation(self, name,address, municipal_entity, denomination, size,website,sf_member_status="Unknown"):
        '''
        Inserts a congregation into the congregations table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        name: string, name of congregation
        address: string, address of congregation
        municipal entity: string
        denomination: string, religous denomination of congregation
        size: integer
        website: string, url of congregation's website
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO congregations (name, address,municipal_entity, denomination, size,website,sf_member_status)
            VALUES (%s, %s, %s,%s, %s, %s, %s);
        """, (name, address,municipal_entity, denomination, size, website,sf_member_status))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
    
    def insert_contact(self, congregation_id,name,role,email,phone_number):
        '''
        Inserts a contact into the contacts table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from congregations table
        name: string, name of contact
        email: string, contact's email
        phone_number: string, contact's phone number
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Contacts (congregation_id, name, role, email,phone_number)
            VALUES (%s, %s, %s,%s,%s);
        """, (congregation_id, name, role,email,phone_number))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()    
    
    def insert_facility(self, congregation_id,facility_size, year_built,heating_sys, vent_sys, ac_sys,est_electric_bill=None):
        '''
        Inserts a facility into the facilities table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from congregations table
        facility_size: int, size of facility in square feet
        year_built: int, year the building was built
        heating_sys: string, type of heating system the facility uses
        venting_sys: string, type of ventilation system the facility uses
        ac_sys: string, type of heating ac system the facility uses
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        if est_electric_bill==None and not facility_size==None:
           est_electric_bill=1.38*facility_size
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO facilities (congregation_id, facility_size,year_built, heating_sys, vent_sys, ac_sys,est_electric_bill)
            VALUES (%s,%s,%s,%s,%s,%s,%s);
        """, (congregation_id, facility_size, year_built, heating_sys, vent_sys, ac_sys,est_electric_bill))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
    
    def insert_addition(self, congregation_id,addition_size, addition_date):
        '''
        Inserts a congregation into the congres tabel
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from congregations table
        addition_size: int, size of addition in square feet
        addition_date: datetime, date addition was adde
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO additions (congregation_id, addition_size,addition_date)
            VALUES (%s,%s,%s);
        """, (congregation_id, addition_size,addition_date))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
        
    def insert_solar_potential(self, congregation_id,usable_sunlight,solar_panel_space,savings,co2_savings):
        '''
        Inserts a congregation into the congres tabel
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from congregations table
        usable_sunlight: int, amount of usable sunlight per year(hours)
        solar_panel_space: int, amount of space to put solar panels
        savings: int, amount of savings ($)
        co2_savings: int, amount of co2 savings/year(metric tons)
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO solar_potential (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings)
            VALUES (%s,%s,%s,%s,%s);
        """, (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
          
    def insert_climate_work(self, congregation_id,work_type,start_date,end_date,description, impact):
        '''
        Inserts climate work into the climate work table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from congregations table
        work_type: string, category of climate work
        start_date: datetime, date the climate work started
        end_date: datetime, date the climate work ended
        description: string, description of climate work
        impact: string, description of climate work impact
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO climate_work (congregation_id, work_type,start_date,end_date,description,impact)
            VALUES (%s,%s,%s,%s,%s,%s);
        """, (congregation_id, work_type,start_date,end_date,description,impact))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()   
    
    def insert_user(self, email, password_hash, role,congregation_id=None,approved=False):
        '''
        Summary
        ---------------------------------------------------------------
        Inserts user into the Users table
        
        Parameters
        ------------------------------------------------------------
        :param email: string, user's email
        :param password_hash: string, users password put through hashing function
        :param role: string, date either "user" or "admin"
        :param description: string, description of climate work
        :param congregation_id: int, id of congregation from congregations table
        :param approved: bool, true if user has been approved by and admin
        
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        if approved==1:
           approved=True
        if approved==0:
           approved=False
        try:
            cursor.execute("""
            INSERT INTO users (email, password_hash, role,congregation_id,approved)
            VALUES (%s,%s,%s,%s,%s);
        """, (email, password_hash, role,congregation_id,approved))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
    
    def insert_case_study(self, congregation_id,case_study_path):
        '''
        Summary
        ------------------------------------------------------------
        Inserts a case study into the case study table
        
        Parameters
        ------------------------------------------------------------
        :param congregation_id: int, id of congregation from congregations table
        :param case_study_path: string, path to case study image
        
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO case_studies (congregation_id,case_study_path)
            VALUES (%s,%s);
        """, (congregation_id,case_study_path))
            conn.commit()
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        conn.close()
     
    def get_congregation_by_id(self,congregation_id):
      query = """
        SELECT  congregation_id, name, address, 
               municipal_entity,denomination, size ,website, sf_member_status 
        FROM congregations
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
      
      congs ={
            "congregation_id": rows[0][0],
            "name": rows[0][1],
            "address": rows[0][2],
            "municipal_entity": rows[0][3],
            "denomination": rows[0][4],
            "size": rows[0][5],
            "website": rows[0][6],
            "sf_member_status": rows[0][7]
        }
      return congs  
    
    def normalize(self,name):
     return re.sub(r"[^a-z0-9]", "", name.lower())

    def get_congregation_id(self, congregation_name):
     if not congregation_name:
        raise ValueError("congregation_name cannot be empty or None")

     normalized_name =  self.normalize(congregation_name)

     query = """
        SELECT congregation_id
        FROM congregations
        WHERE REGEXP_REPLACE(LOWER(name), '[^a-z0-9]', '', 'g') = %s
      """

     with psycopg2.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (normalized_name,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                raise ValueError(
                    f"No congregation found with name '{congregation_name}' (normalized: '{normalized_name}')"
                )
    
    def get_case_study_by_cong_id(self,congregation_id):
      query = """
        SELECT  case_study_id, congregation_id, case_study_path
        FROM case_studies
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
    
      cs = []
      for row in rows:
        cs.append({
            "case_study_id": row[0],
            "congregation_id": row[1],
            "case_study_path": row[2],
        })
      return cs
    
    def get_contact_by_id(self, contact_id):
      query = """
        SELECT contact_id, congregation_id, name, role, email, phone_number
        FROM contacts
        WHERE contact_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (contact_id,))
      row = cursor.fetchone()
     
      
      contact ={
            "contact_id": row[0],
            "congregation_id": row[1],
            "name": row[2],
            "role": row[3],
            "email": row[4],
            "phone_number": row[5],
        }

      return contact
    
    
    def get_facility_by_id(self, facility_id):
      query = """
        SELECT facility_id, congregation_id, facility_size, year_built, 
               heating_sys, vent_sys, ac_sys, est_electric_bill
        FROM facilities
        WHERE facility_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (facility_id,))
      row = cursor.fetchone()
     
      
      facility ={
            "facility_id": row[0],
            "congregation_id": row[1],
            "facility_size": row[2],
            "year_built": row[3],
            "heating_sys": row[4],
            "vent_sys": row[5],
            "ac_sys": row[6],
            "est_electric_bill": row[7],
        }

      return facility
    
    def get_addition_by_id(self, addition_id):
     
      query = """
        SELECT addition_id , congregation_id, addition_size,addition_date 
        FROM additions
        WHERE addition_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (addition_id,))
      row = cursor.fetchone()

      
      addition = {
            "addition_id": row[0],
            "congregation_id": row[1],
            "addition_size": row[2],
            "addition_date": row[3],
        }

      return addition
    
    def get_solar_by_id(self, solar_pot_id):
      query = """
        SELECT solar_pot_id, congregation_id, usable_sunlight,solar_panel_space,
         savings, co2_savings
        FROM solar_potential
        WHERE solar_pot_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (solar_pot_id,))
      row= cursor.fetchone()

      
      solar = {
            "solar_pot_id": row[0],
            "congregation_id": row[1],
            "usable_sunlight": row[2],
            "solar_panel_space": row[3],
            "savings": row[4],
            "co2_savings": row[5],
        }

      return solar
    
    def get_climate_work_by_id(self, climate_work_id):
      query = """
        SELECT climate_work_id, congregation_id, work_type,start_date,end_date,
         description, impact
        FROM climate_work
        WHERE climate_work_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (climate_work_id,))
      row = cursor.fetchone()

      
      work ={
            "climate_work_id": row[0],
            "congregation_id": row[1],
            "work_type": row[2],
            "start_date": row[3],
            "end_date": row[4],
            "description": row[5],
            "impact": row[6],
        }

      return work
    
    def get_contacts_by_congregation(self, congregation_id):
      query = """
        SELECT contact_id, congregation_id, name, role, email, 
               phone_number
        FROM contacts
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
      
      contacts = []
      for row in rows:
        contacts.append({
            "contact_id": row[0],
            "congregation_id": row[1],
            "name": row[2],
            "role": row[3],
            "email": row[4],
            "phone_number": row[5],
        })

      return contacts
    
    def get_facilities_by_congregation(self, congregation_id):
      query = """
        SELECT facility_id, congregation_id, facility_size, year_built, 
               heating_sys, vent_sys, ac_sys, est_electric_bill
        FROM facilities
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
      
      facilities = []
      for row in rows:
        facilities.append({
            "facility_id": row[0],
            "congregation_id": row[1],
            "facility_size": row[2],
            "year_built": row[3],
            "heating_sys": row[4],
            "vent_sys": row[5],
            "ac_sys": row[6],
            "est_electric_bill": row[7],
        })

      return facilities
    
    def get_additions_by_congregation(self, congregation_id):
     
      query = """
        SELECT addition_id , congregation_id, addition_size,addition_date 
        FROM additions
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()

      
      additions = []
      for row in rows:
        additions.append({
            "addition_id": row[0],
            "congregation_id": row[1],
            "addition_size": row[2],
            "addition_date": row[3],
        })

      return additions
    
    def get_solar_by_congregation(self, congregation_id):
      query = """
        SELECT solar_pot_id, congregation_id, usable_sunlight,solar_panel_space,
         savings, co2_savings
        FROM solar_potential
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()

      
      solar = []
      for row in rows:
        solar.append({
            "solar_pot_id": row[0],
            "congregation_id": row[1],
            "usable_sunlight": row[2],
            "solar_panel_space": row[3],
            "savings": row[4],
            "co2_savings": row[5],
        })

      return solar
    
    def get_climate_work_by_congregation(self, congregation_id):
      query = """
        SELECT climate_work_id, congregation_id, work_type,start_date,end_date,
         description, impact
        FROM climate_work
        WHERE congregation_id = %s
      """
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()

      
      work = []
      for row in rows:
        work.append({
            "climate_work_id": row[0],
            "congregation_id": row[1],
            "work_type": row[2],
            "start_date": row[3],
            "end_date": row[4],
            "description": row[5],
            "impact": row[6],
        })

      return work
    
    def update_congregation(self, cong_id, data):
     if not(data["size"] and data["size"].isdigit()):
       data["size"]=0
     query = """
        UPDATE congregations
        SET name = %s, address = %s, municipal_entity = %s, denomination = %s,
            size = %s, website = %s, sf_member_status=%s
        WHERE congregation_id = %s
     """
     print(data)
     values = (
        data["name"], data["address"], data["municipal_entity"],
        data["denomination"], data["size"], data["website"], data["sf_member_status"], cong_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_contact(self, contact_id, data):
        
     query = """
        UPDATE contacts
        SET name= %s, role = %s, email= %s, phone_number = %s
        WHERE contact_id = %s
     """
     
     values = (
        data["name"], data["role"], data["email"],
        data["phone_number"], contact_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_facility(self, facility_id, data):
        
     if not(data["facility_size"] and data["facility_size"].isdigit()):
       data["facility_size"]=0
     if not(data["year_built"] and data["year_built"].isdigit()):
       data["year_built"]=0
     if not(data["est_electric_bill"] and data["est_electric_bill"].isdigit()):
       data["est_electric_bill"]=0
     query = """
        UPDATE facilities
        SET facility_size = %s, year_built = %s, heating_sys= %s, vent_sys = %s,
            ac_sys = %s, est_electric_bill = %s
        WHERE facility_id = %s
     """
     
     values = (
        data["facility_size"], data["year_built"], data["heating_sys"],
        data["vent_sys"], data["ac_sys"], data["est_electric_bill"], facility_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_addition(self, addition_id, data):
     if not(data["addition_size"] and data["addition_size"].isdigit())==None:
       data["addition_size"]=0
     query = """
        UPDATE additions
        SET addition_size = %s, addition_date = %s
        WHERE addition_id = %s
     """
     
     values = (
        data["addition_size"], data["addition_date"], addition_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_solar(self, solar_pot_id, data):
     if not(data["usable_sunlight"] and data["usable_sunlight"].isdigit()):
       data["usable_sunlight"]=0
     if not(data["solar_panel_space"] and data["solar_panel_space"].isdigit()):
       data["solar_panel_space"]=0
     if not(data["savings"] and data["savings"].isdigit()):
       data["savings"]=0
     if not(data["co2_savings"] and data["co2_savings"].isdigit()):
       data["co2_savings"]=0
     query = """
        UPDATE solar_potential
        SET usable_sunlight = %s, solar_panel_space = %s, savings= %s, co2_savings = %s
        WHERE solar_pot_id = %s
     """
     
     values = (
        data["usable_sunlight"], data["solar_panel_space"], data["savings"],
        data["co2_savings"], solar_pot_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_climate_work(self, climate_work_id, data):
     query = """
        UPDATE climate_work
        SET work_type = %s, start_date = %s, end_date= %s, description = %s,
            impact = %s
        WHERE climate_work_id = %s
     """
     
     values = (
        data["work_type"], data["start_date"], data["end_date"],
        data["description"], data["impact"], climate_work_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
    
    def update_case_study(self, congregation_id, case_study_path):
     query = """
        UPDATE case_studies
        SET case_study= %s
        WHERE climate_work_id = %s
     """
     
     values = (
       case_study_path, congregation_id
    )

     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
     conn.close()
   
    def delete_congregation(self, cong_id):
     
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     try:
        cur.execute(
            "DELETE FROM congregations WHERE congregation_id = %s",
            (cong_id,)
        )
        conn.commit()
     except psycopg2.Error as e:
        print(f"Error deleting congregation {cong_id}: {e}")
        conn.rollback()

     finally:
        conn.close()
    
    def delete_contact(self, contact_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
     conn.commit()
     conn.close()

    def delete_facility(self, facility_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM facilities WHERE facility_id = %s", (facility_id,))
     conn.commit()
     conn.close()
   
    def delete_addition(self, addition_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM additions WHERE addition_id = %s", (addition_id,))
     conn.commit()
     conn.close()
    
    def delete_Solar_Potential(self, solar_pot_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM solar_potential WHERE solar_pot_id = %s", (solar_pot_id,))
     conn.commit()
     conn.close()
    
    def delete_Climate_Work(self, climate_work_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM climate_work WHERE climate_work_id = %s", (climate_work_id,))
     conn.commit()
     conn.close()
    
    def delete_User(self, user_id):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
     conn.commit()
     conn.close()
    
    def delete_case_study(self, case_study_id):
     
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     try:
        cur.execute(
            "DELETE FROM case_studies WHERE case_study_id = %s",
            (case_study_id,)
        )
        conn.commit()
     except psycopg2.Error as e:
        print(f"Error deleting case study {case_study_id}: {e}")
        conn.rollback()

     finally:
        conn.close()
    
    def drop_table(self,table_name):
        '''
        removes a table from the database
        ----------------------------------
        Parameters
        ----------------------------------
        table_name: string, name of table
        '''
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(drop_table_sql)
        conn.commit()
        conn.close()
    
    def get_all_congregations(self):
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cursor.execute("SELECT congregation_id,name FROM congregations ORDER BY name")
        rows = cursor.fetchall()
        # Convert to list of dicts 
        return [{"congregation_id": row[0],"name": row[1]} for row in rows]
    
    def get_all_case_study_cong_ids(self):
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT C.congregation_id,C.name FROM congregations C INNER JOIN case_studies CS ON CS.congregation_id=C.congregation_id ORDER BY C.name")
        rows = cursor.fetchall()
        # Convert to list of dicts 
        return [{"congregation_id": row[0],"name": row[1]} for row in rows]
    
    def get_user_by_email(self, email):
        return self.fetchone(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

    def get_user_by_id(self, user_id):
        row=self.fetchone(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        print("DEBUG ROW:", row)
        return row
    
    def get_user_id(self,email):
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cursor = conn.cursor()
      try:
         cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
         )
         result = cursor.fetchone()
         if result:
            return result[0]  # first column = user_id
         else:
            return None
      except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    def get_admin_emails(self):
      rows = self.fetchall("SELECT email FROM users WHERE role = 'admin'")
      return [r[0] for r in rows] 
    
    def approve_user(self, user_id):
      conn = psycopg2.connect(os.environ["DATABASE_URL"])
      cur = conn.cursor()
      cur.execute("UPDATE users SET approved = TRUE WHERE id = %s", (user_id,))
      conn.commit()
      conn.close()
    
    def close(self):
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()
        cursor.close()
        conn.close()
    
    def fetchone(self, query, params=()):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, params)
     row = cur.fetchone()
     conn.close()
     return row
     
    def fetchall(self, query, params=()):
     conn = psycopg2.connect(os.environ["DATABASE_URL"])
     cur = conn.cursor()
     cur.execute(query, params)
     row = cur.fetchall()
     conn.close()
     return row