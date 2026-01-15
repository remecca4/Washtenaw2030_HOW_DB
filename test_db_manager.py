from db_manager import DatabaseManager
from datetime import datetime
db_manage=DatabaseManager()
cong1_id=db_manage.insert_congregation("cong1","3211 nweiwe iwjlk","Ann Arbor","Jewish","200","cong1@gmail.com","7498327478","cong1.com")
#db_manage.insert_facility("cong1",150,60,"heat","vent","ac")
#db_manage.insert_addition("cong1",50,datetime(2000,12,1))
#db_manage.insert_solar_potential("cong1",1000,100,400,5)
#db_manage.insert_climate_work("cong1","tree planting",datetime(2010,10,5),datetime(2011,10,5),"planted trees","planted 52 trees")
db_manage.insert_user("remecca4@gmail.com","1234","admin",None)
all_congs=db_manage.get_all_congregations()
print(all_congs)
