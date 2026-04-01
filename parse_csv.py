from db_manager import DatabaseManager
from datetime import datetime
import csv


db = DatabaseManager()

def safe_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val.strip(), "%m/%d/%Y")
    except:
        return None

def parse_insert_congregation_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          try:
            name = row.get('Congregation', '').strip()
            address = row.get('Address', '').strip() or None
            municipal_entity = row.get('Municipal Entity', '').strip() or None
            denomination = row.get('Denomination', '').strip() or None

            size_raw = row.get('Size', '').strip()
            size = int(size_raw) if size_raw.isdigit() else None


            website_raw = row.get('Website', '').strip().lower()

            if not website_raw or 'no website' in website_raw:
                website = None
            else:
                if '(' in website_raw and 'http' in website_raw:
                    website = website_raw[website_raw.find('http'):]
                else:
                    website = row.get('Website').strip()

            db.insert_congregation(name, address, municipal_entity, denomination, size, website)
          except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue
def parse_insert_contacts_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          try:
            cong_name = row.get('Congregation', '').strip()
            id=db.get_congregation_id(cong_name)
            name=row.get('Name', '').strip() or None
            role = row.get('Role', '').strip() or None
            email = row.get('Email', '').strip() or None
            phone_number= row.get('Phone Number', '').strip() or None

            db.insert_contact(id, name,role, email, phone_number)
          except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue
def parse_insert_facilities_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
           try:

            name = row.get('Congregation', '').strip()
            id=db.get_congregation_id(name)
            facility_size = row.get('Facility size', '').strip()
            facility_size = int(facility_size) if facility_size.isdigit() else None

            yb = row.get('Year Built', '').strip()
            yb = int(yb) if yb.isdigit() else None

            heat_system = row.get('Heating System', '').strip() or None
            vent_system = row.get('Vent System', '').strip() or None
            ac_system = row.get('AC System', '').strip() or None

            db.insert_facility(id, facility_size, yb, heat_system, vent_system, ac_system)
           except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue

def parse_insert_additions_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          try:
            name = row.get('Congregation', '').strip()
            id=db.get_congregation_id(name)

            addition_size = row.get('Addition size', '').strip()
            addition_size = int(addition_size) if addition_size.isdigit() else None

            addition_date = safe_date(row.get('Addition date'))

            db.insert_addition(id, addition_size, addition_date)
          except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue

def parse_insert_solar_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          try:
            name = row.get('Congregation', '').strip()
            id=db.get_congregation_id(name)

            usable_sunlight = row.get('Usable Sunlight', '').strip()
            usable_sunlight = int(usable_sunlight) if usable_sunlight.isdigit() else None

            solar_panel_space = row.get('Solar Panel Space', '').strip()
            solar_panel_space = int(solar_panel_space) if solar_panel_space.isdigit() else None

            savings = row.get('Savings', '').strip()
            savings = int(savings) if savings.isdigit() else None

            co2_savings = row.get('CO2 Savings', '').strip()
            co2_savings = int(co2_savings) if co2_savings.isdigit() else None

            db.insert_solar_potential(id, usable_sunlight, solar_panel_space, savings, co2_savings)
          except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue

def parse_insert_climate_work_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          try:
            name = row.get('Congregation', '').strip()
            id=db.get_congregation_id(name)

            work_type = row.get('Work Type', '').strip()

            start_date = safe_date(row.get('Start Date'))
            end_date   = safe_date(row.get('End Date'))

            description = row.get('Description', '').strip() or None
            impact = row.get('Impact', '').strip() or None

            db.insert_climate_work(id, work_type, start_date, end_date, description, impact)
          except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue

if __name__ == "__main__":
    parse_insert_congregation_csv("congregations.csv")
    db.close()