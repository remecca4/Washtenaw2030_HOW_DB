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
     FOREIGN KEY (congregation_id) REFERENCES congregations(congregation_id)
    
     );
      -- Table to track any additions to facilities
     CREATE TABLE IF NOT EXISTS Additions (
     addition_id INTEGER PRIMARY KEY AUTOINCREMENT,
     facility_id INTEGER NOT NULL,
     addition_size INTEGER, --size of the addition (sq ft.)
     addition_date DATETIME, --date addition was added
     FOREIGN KEY (facility_id) REFERENCES facilities(facility_id)
    
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
     
    