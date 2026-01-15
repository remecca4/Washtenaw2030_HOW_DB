import sqlite3


class DatabaseManager:
    def __init__(self, db_path='how_db.db'):
        '''
         Database Manager Constructor
         -------------------------------------
         Parameters
         ------------------------------------
         db_path: string, path to database
        '''
        self.db_path = db_path
        self._setup_database()
        
        
    def get_connection(self):
         conn = sqlite3.connect(self.db_path)
         conn.execute("PRAGMA foreign_keys = ON;")
         conn.row_factory = sqlite3.Row
         return conn
        
    def _setup_database(self):
        '''
         Database Manager Constructor
         -------------------------------------
         executes script to set up HOW database
        '''
        schema_script = """
        -- Table to store basic info about houses of worship
        CREATE TABLE IF NOT EXISTS Congregations (
        congregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        municipal_entity TEXT, -- eg. Ann Arbor, Chelsea, etc.
        denomination TEXT,
        size INTEGER,  -- amount of people in the HOW
        email TEXT,  
        phone_number TEXT,
        website TEXT
       );

      
     -- Table to keep track of facility info
     CREATE TABLE IF NOT EXISTS Facilities (
     facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
     congregation_id INTEGER NOT NULL,
     facility_size INTEGER, --size of the facility (sq ft.)
     age INTEGER, --age of building
     heating_sys TEXT, --heating system type
     vent_sys  TEXT, --ventilation system type
     ac_sys TEXT,  --ac system type
     est_electric_bill FLOAT,  --estimated electric bill
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
      ON DELETE CASCADE
    
     );
      -- Table to track any additions to facilities
     CREATE TABLE IF NOT EXISTS Additions (
     addition_id INTEGER PRIMARY KEY AUTOINCREMENT,
     congregation_id INTEGER NOT NULL,
     addition_size INTEGER, --size of the addition (sq ft.)
     addition_date DATETIME, --date addition was added
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
      ON DELETE CASCADE
    
     );
  -- Table to record each congregation's solar potential
     CREATE TABLE IF NOT EXISTS Solar_potential (
     solar_pot_id INTEGER PRIMARY KEY AUTOINCREMENT,
     congregation_id INTEGER NOT NULL,
     usable_sunlight INTEGER, --est amount of usable sunlight per year in hours
     solar_panel_space INTEGER, --amount of space for solar panels (sq ft.)
     savings INTEGER, --estimated amount of monetary savings per year from installing solar panels(dollars)
     co2_savings INTEGER, --estimated CO2 savings per year from installing solar panels(metric tons)
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
      ON DELETE CASCADE
    
     );
     -- Tracks any climate work each congregation has done
     CREATE TABLE IF NOT EXISTS Climate_work(
     climate_work_id INTEGER PRIMARY KEY AUTOINCREMENT,
     congregation_id INTEGER NOT NULL,
     work_type TEXT NOT NULL, --category of climate work
     start_date DATETIME, --start date of work
     end_date DATETIME, --end date of work (leave blank if still ongoing)
     description  TEXT, --description of work
     impact TEXT,  --add any impacts here
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
      ON DELETE CASCADE
    
     );
    CREATE TABLE IF NOT EXISTS Users (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     email TEXT UNIQUE NOT NULL,
     password_hash TEXT NOT NULL,
     role TEXT NOT NULL,
     congregation_id INTEGER,
     FOREIGN KEY (congregation_id) REFERENCES Congregations(congregation_id)
     ON DELETE CASCADE
);
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.executescript(schema_script)
        connection.commit()

    def clear_tables(self):
        '''
        clears all tables in database
        '''
        truncate_script = """
        DELETE FROM Congregations;
        DELETE FROM Facilities;
        DELETE FROM Additions;
        DELETE FROM Solar_potential;
        DELETE FROM Climate_work;
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.executescript(truncate_script)
        connection.commit()
        print("CLEAR TABLES")

    def insert_congregation(self, name,address, municipal_entity, denomination, size, email,phone_number,website):
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
        email: string, congregation's email
        phone_number: string, congregation's phone number
        website: string, url of congregation's website
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
       
        try:
            cursor.execute("""
            INSERT INTO Congregations (name, address,municipal_entity, denomination, size, email,phone_number,website)
            VALUES (?, ?, ?,?, ?, ?,?,?);
        """, (name, address,municipal_entity, denomination, size, email,phone_number,website))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return cursor.lastrowid

    def insert_facility(self, congregation_id,facility_size, age,heating_sys, vent_sys, ac_sys):
        '''
        Inserts a facility into the facilities table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from Congregations table
        facility_size: int, size of facility in square feet
        age: int, age of facility in years
        heating_sys: string, type of heating system the facility uses
        venting_sys: string, type of ventilation system the facility uses
        ac_sys: string, type of heating ac system the facility uses
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Facilities (congregation_id, facility_size,age, heating_sys, vent_sys, ac_sys,est_electric_bill)
            VALUES (?,?,?,?,?,?,?);
        """, (congregation_id, facility_size,age, heating_sys, vent_sys, ac_sys,1.38*facility_size))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    
    def insert_addition(self, congregation_id,addition_size, addition_date):
        '''
        Inserts a congregation into the congres tabel
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from Congregations table
        addition_size: int, size of addition in square feet
        addition_date: datetime, date addition was adde
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Additions (congregation_id, addition_size,addition_date)
            VALUES (?,?,?);
        """, (congregation_id, addition_size,addition_date))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return cursor.lastrowid
    
    def insert_solar_potential(self, congregation_id,usable_sunlight,solar_panel_space,savings,co2_savings):
        '''
        Inserts a congregation into the congres tabel
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from Congregations table
        usable_sunlight: int, amount of usable sunlight per year(hours)
        solar_panel_space: int, amount of space to put solar panels
        savings: int, amount of savings ($)
        co2_savings: int, amount of co2 savings/year(metric tons)
        --------------------------------------------------
        Returns
        --------------------------------------------------
        int, last row id
        '''
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Solar_potential (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings)
            VALUES (?,?,?,?,?);
        """, (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return cursor.lastrowid
    
    def insert_climate_work(self, congregation_id,work_type,start_date,end_date,description, impact):
        '''
        Inserts climate work into the climate work table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from Congregations table
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
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Climate_work (congregation_id, work_type,start_date,end_date,description,impact)
            VALUES (?,?,?,?,?,?);
        """, (congregation_id, work_type,start_date,end_date,description,impact))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return cursor.lastrowid
    
    def insert_user(self, email, password_hash, role,congregation_id):
        '''
        Inserts climate work into the climate work table
        ------------------------------------------------------------
        Parameters
        ------------------------------------------------------------
        congregation_id: int, id of congregation from Congregations table
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
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO Users (email, password_hash, role,congregation_id)
            VALUES (?,?,?,?);
        """, (email, password_hash, role,congregation_id))
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def get_congregation_id(self,congregation_name):
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
      try:
         cursor.execute(
            "SELECT congregation_id FROM Congregations WHERE name = ?",
            (congregation_name,)
         )
         result = cursor.fetchone()
         if result:
            return result[0]  # first column = congregation_id
         else:
            return None
      except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
     
    def get_congregation_by_id(self,congregation_id):
      query = """
        SELECT  congregation_id, name, address, 
               municipal_entity,denomination, size, email,phone_number,website 
        FROM Congregations
        WHERE congregation_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
      
      congs ={
            "congregation_id": rows[0][0],
            "name": rows[0][1],
            "address": rows[0][2],
            "municipal_entity": rows[0][3],
            "denomination": rows[0][4],
            "size": rows[0][5],
            "email": rows[0][6],
            "phone_number": rows[0][7],
            "website": rows[0][8],
        }
      return congs  
    
    def get_facility_by_id(self, facility_id):
      query = """
        SELECT facility_id, congregation_id, facility_size, age, 
               heating_sys, vent_sys, ac_sys, est_electric_bill
        FROM Facilities
        WHERE facility_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
      cursor.execute(query, (facility_id,))
      row = cursor.fetchone()
     
      
      facility ={
            "facility_id": row[0],
            "congregation_id": row[1],
            "facility_size": row[2],
            "age": row[3],
            "heating_sys": row[4],
            "vent_sys": row[5],
            "ac_sys": row[6],
            "est_electric_bill": row[7],
        }

      return facility
    
    def get_addition_by_id(self, addition_id):
     
      query = """
        SELECT addition_id , congregation_id, addition_size,addition_date 
        FROM Additions
        WHERE addition_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
        FROM Solar_potential
        WHERE solar_pot_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
        FROM Climate_work
        WHERE climate_work_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
    
    def get_facilities_by_congregation(self, congregation_id):
      query = """
        SELECT facility_id, congregation_id, facility_size, age, 
               heating_sys, vent_sys, ac_sys, est_electric_bill
        FROM Facilities
        WHERE congregation_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
      cursor.execute(query, (congregation_id,))
      rows = cursor.fetchall()
     
      
      facilities = []
      for row in rows:
        facilities.append({
            "facility_id": row[0],
            "congregation_id": row[1],
            "facility_size": row[2],
            "age": row[3],
            "heating_sys": row[4],
            "vent_sys": row[5],
            "ac_sys": row[6],
            "est_electric_bill": row[7],
        })

      return facilities
    
    def get_additions_by_congregation(self, congregation_id):
     
      query = """
        SELECT addition_id , congregation_id, addition_size,addition_date 
        FROM Additions
        WHERE congregation_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
        FROM Solar_potential
        WHERE congregation_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
        FROM Climate_work
        WHERE congregation_id = ?
      """
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
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
     query = """
        UPDATE Congregations
        SET name = ?, address = ?, municipal_entity = ?, denomination = ?,
            size = ?, email = ?, phone_number = ?, website = ?
        WHERE congregation_id = ?
     """
     values = (
        data["name"], data["address"], data["municipal_entity"],
        data["denomination"], data["size"], data["email"],
        data["phone_number"], data["website"], cong_id
    )

     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
    
    def update_facility(self, facility_id, data):
     query = """
        UPDATE Facilities
        SET facility_size = ?, age = ?, heating_sys= ?, vent_sys = ?,
            ac_sys = ?, est_electric_bill = ?
        WHERE facility_id = ?
     """
     
     values = (
        data["facility_size"], data["age"], data["heating_sys"],
        data["vent_sys"], data["ac_sys"], data["est_electric_bill"], facility_id
    )

     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
    
    def update_addition(self, addition_id, data):
     query = """
        UPDATE Additions
        SET addition_size = ?, addition_date = ?
        WHERE addition_id = ?
     """
     
     values = (
        data["addition_size"], data["addition_date"], addition_id
    )

     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
    
    def update_solar(self, solar_pot_id, data):
     query = """
        UPDATE Solar_Potential
        SET usable_sunlight = ?, solar_panel_space = ?, savings= ?, co2_savings = ?
        WHERE solar_pot_id = ?
     """
     
     values = (
        data["usable_sunlight"], data["solar_panel_space"], data["savings"],
        data["co2_savings"], solar_pot_id
    )

     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
    
    def update_climate_work(self, climate_work_id, data):
     query = """
        UPDATE Climate_Work
        SET work_type = ?, start_date = ?, end_date= ?, description = ?,
            impact = ?
        WHERE climate_work_id = ?
     """
     
     values = (
        data["work_type"], data["start_date"], data["end_date"],
        data["description"], data["impact"], climate_work_id
    )

     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, values)
     conn.commit()
    
    def delete_congregation(self, cong_id):
     
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     try:
        # Delete facilities
        for f in self.get_facilities_by_congregation(cong_id):
            self.delete_facility(f["facility_id"])

        # Delete additions
        for a in self.get_additions_by_congregation(cong_id):
            self.delete_addition(a["addition_id"])

        # Delete solar potential entries
        for s in self.get_solar_by_congregation(cong_id):
            self.delete_Solar_Potential(s["solar_pot_id"])

        # Delete climate work
        for cw in self.get_climate_work_by_congregation(cong_id):
            self.delete_Climate_Work(cw["climate_work_id"])

        # Finally delete the congregation
        cur.execute(
            "DELETE FROM Congregations WHERE congregation_id = ?",
            (cong_id,)
        )
        conn.commit()

     except sqlite3.Error as e:
        print(f"Error deleting congregation {cong_id}: {e}")
        conn.rollback()

     finally:
        conn.close()
    
    def delete_facility(self, facility_id):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute("DELETE FROM Facilities WHERE facility_id = ?", (facility_id,))
     conn.commit()
    
    def delete_addition(self, addition_id):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute("DELETE FROM Additions WHERE addition_id = ?", (addition_id,))
     conn.commit()
    
    def delete_Solar_Potential(self, solar_pot_id):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute("DELETE FROM Solar_Potential WHERE solar_pot_id = ?", (solar_pot_id,))
     conn.commit()
    
    def delete_Climate_Work(self, climate_work_id):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute("DELETE FROM Climate_Work WHERE climate_work_id = ?", (climate_work_id,))
     conn.commit()
    
    def delete_User(self, user_id):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute("DELETE FROM Users WHERE id = ?", (user_id,))
     conn.commit()
    
    def drop_table(self,table_name):
        '''
        removes a table from the database
        ----------------------------------
        Parameters
        ----------------------------------
        table_name: string, name of table
        '''
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(drop_table_sql)
        connection.commit()
    
    def get_all_congregations(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT congregation_id,name FROM Congregations")
        rows = cursor.fetchall()
        # Convert to list of dicts 
        return [{"congregation_id": row[0],"name": row[1]} for row in rows]
    
    def get_user_by_email(self, email):
        return self.fetchone(
            "SELECT * FROM Users WHERE email = ?",
            (email,)
        )

    def get_user_by_id(self, user_id):
        return self.fetchone(
            "SELECT * FROM Users WHERE id = ?",
            (user_id,)
        )
    def get_user_id(self,email):
      connection = sqlite3.connect(self.db_path)
      cursor = connection.cursor()
      try:
         cursor.execute(
            "SELECT id FROM Users WHERE email = ?",
            (email,)
         )
         result = cursor.fetchone()
         if result:
            return result[0]  # first column = user_id
         else:
            return None
      except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
       
    def close(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.close()
        connection.close()
    
    def fetchone(self, query, params=()):
     conn = sqlite3.connect(self.db_path)
     cur = conn.cursor()
     cur.execute(query, params)
     row = cur.fetchone()
     conn.close()
     return row