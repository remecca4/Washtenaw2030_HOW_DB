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
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self._setup_database()
        #self.clear_tables()
        #self.cursor.execute("PRAGMA table_info(mission_waypoints)")
        print(self.cursor.fetchall())
        
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
        name TEXT NOT NULL,
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
    
     );
      -- Table to track any additions to facilities
     CREATE TABLE IF NOT EXISTS Additions (
     addition_id INTEGER PRIMARY KEY AUTOINCREMENT,
     congregation_id INTEGER NOT NULL,
     addition_size INTEGER, --size of the addition (sq ft.)
     addition_date DATETIME, --date addition was added
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
    
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
    
     );
     
        """
        self.cursor.executescript(schema_script)
        self.connection.commit()

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
        self.cursor.executescript(truncate_script)
        self.connection.commit()
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

        try:
            self.cursor.execute("""
            INSERT INTO Congregations (name, address,municipal_entity, denomination, size, email,phone_number,website)
            VALUES (?, ?, ?,?, ?, ?,?,?);
        """, (name, address,municipal_entity, denomination, size, email,phone_number,website))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return self.cursor.lastrowid

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

        try:
            self.cursor.execute("""
            INSERT INTO Facilities (congregation_id, facility_size,age, heating_sys, vent_sys, ac_sys)
            VALUES (?,?,?,?,?,?,?);
        """, (congregation_id, facility_size,age, heating_sys, vent_sys, ac_sys,1.38*facility_size))
            self.connection.commit()
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

        try:
            self.cursor.execute("""
            INSERT INTO Additions (congregation_id, addition_size,addition_date)
            VALUES (?,?,?);
        """, (congregation_id, addition_size,addition_date))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return self.cursor.lastrowid
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

        try:
            self.cursor.execute("""
            INSERT INTO Solar_potential (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings)
            VALUES (?,?,?,?,?);
        """, (congregation_id, usable_sunlight,solar_panel_space,savings,co2_savings))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return self.cursor.lastrowid
    def insert_climate_work(self, congregation_id,work_type,start_date,end_date,description, impact):
        '''
        Inserts a congregation into the congres tabel
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

        try:
            self.cursor.execute("""
            INSERT INTO Climate_work (congregation_id, work_type,start_date,end_date,description,impact)
            VALUES (?,?,?,?,?,?);
        """, (congregation_id, work_type,start_date,end_date,description,impact))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        
        return self.cursor.lastrowid
  

    def get_congregation_id(self,congregation_name):
      try:
         self.cursor.execute(
            "SELECT congregation_id FROM Congregations WHERE name = ?",
            (congregation_name,)
         )
         result = self.cursor.fetchone()
         if result:
            return result[0]  # first column = congregation_id
         else:
            return None
      except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    def drop_table(self,table_name):
        '''
        removes a table from the database
        ----------------------------------
        Parameters
        ----------------------------------
        table_name: string, name of table
        '''
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(drop_table_sql)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()