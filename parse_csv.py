from db_manager import DatabaseManager
from datetime import datetime
import csv
db=DatabaseManager()
def parse_insert_congregation_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Congregation').strip() or None
            address = row.get('Address').strip() or None
            municipal_entity = row.get('Municipal Entity').strip() or None
            denomination = row.get('Denomination').strip() or None

            # Handle size: convert to int if possible
            size_raw = row.get('Size').strip()
            size = int(size_raw) if size_raw.isdigit() else None

            email = row.get('Email').strip() or None
            phone_number = row.get('Phone Number').strip() or None
            website_raw = row.get('Website').strip().lower()
            
            # Clean website field
            if not website_raw or 'no website' in website_raw:
                website = None
            else:
                # Some entries have "no website (facebook: URL)"
                if '(' in website_raw and 'http' in website_raw:
                    start = website_raw.find('http')
                    website = website_raw[start:]
                else:
                    website = row.get('Website').strip()

            db.insert_congregation(name, address, municipal_entity, denomination, size, email, phone_number, website)

def parse_insert_facilities_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Congregation').strip() or None
            id=db.get_congregation_id(name)
            
            facility_size = row.get('Facility size').strip() or None
            facility_size=int(facility_size) if facility_size.isdigit() else None
            
            age = row.get('Age').strip() or None
            age=int(age) if age.isdigit() else None
            
            heat_system = row.get('Heating System').strip() or None
            vent_system = row.get('Vent System').strip() or None
            ac_system = row.get('AC System').strip() or None


            db.insert_facility(id,facility_size,age,heat_system,vent_system,ac_system)

def parse_insert_additions_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Congregation').strip() or None
            id=db.get_congregation_id(name)
            
            addition_size = row.get('Addition size').strip() or None
            addition_size=int(addition_size) if addition_size.isdigit() else None
            
            addition_date=row.get('Addition date').strip() or None
            addition_date = datetime.strptime(addition_date, "%m/%d/%Y")
            db.insert_addition(id,addition_size,addition_date)

def parse_insert_solar_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Congregation').strip() or None
            id=db.get_congregation_id(name)
            
            usable_sunlight = row.get('Usable Sunlight').strip() or None
            usable_sunlight=int(usable_sunlight) if usable_sunlight.isdigit() else None
            
            solar_panel_space = row.get('Solar Panel Space').strip() or None
            solar_panel_space=int(solar_panel_space) if solar_panel_space.isdigit() else None

            savings = row.get('Savings').strip() or None
            savings=int(savings) if savings.isdigit() else None
            
            co2_savings = row.get('CO2 Savings').strip() or None
            co2_savings=int(savings) if co2_savings.isdigit() else None
           
            db.insert_solar_potential(id,usable_sunlight,solar_panel_space,savings,co2_savings)

def parse_insert_climate_work_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Congregation').strip() or None
            id=db.get_congregation_id(name)
            
            work_type = row.get('Work Type').strip() or None
            
            start_date=row.get('Start Date').strip() or None
            start_date = datetime.strptime(start_date, "%m/%d/%Y")
            
            end_date=row.get('Start Date').strip() or None
            end_date = datetime.strptime(end_date, "%m/%d/%Y")
            
            description = row.get('Work Type').strip() or None
            impact = row.get('Work Type').strip() or None
            
            db.insert_climate_work(id,work_type,start_date,end_date,description,impact)


if __name__ == "__main__":
    db.clear_tables()
    parse_insert_congregation_csv("congregations.csv")
    db.close()