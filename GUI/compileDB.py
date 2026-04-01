import pickle
from pyexcel_ods import get_data

class Plant():
    tolerance = 0.1
    def __init__(self, name, pH_min, pH_max, ec_min, ec_max,cf_min, 
                 cf_max, ppm700_min, ppm700_max, ppm500_min, ppm500_max,
                 sun_min, sun_max, germ_days, harvest_days, desc):
        self.name = name
        self.pH_min = pH_min
        self.pH_max = pH_max
        if pH_min > pH_max:
            pH_max = pH_min + self.tolerance
            pH_min = pH_min - self.tolerance
        self.ec_min = ec_min
        self.ec_max = ec_max
        self.cf_min = cf_min
        self.cf_max = cf_max
        self.ppm700_min = ppm700_min
        self.ppm700_max = ppm700_max
        self.ppm500_min = ppm500_min
        self.ppm500_max = ppm500_max
        self.sun_min = sun_min
        self.sun_max = sun_max
        self.germ_days = germ_days
        self.harvest_days = harvest_days
        self.desc = desc

data = get_data("hydro_plant_values.ods")
sheet = data['Compiled']
index = 0
plants = []
while sheet[index][0] != 0:
    plant = Plant(sheet[index][0],
                  sheet[index][1],
                  sheet[index][2],
                  sheet[index][3],
                  sheet[index][4],
                  sheet[index][5],
                  sheet[index][6],
                  sheet[index][7],
                  sheet[index][8],
                  sheet[index][9],
                  sheet[index][10],
                  sheet[index][11],
                  sheet[index][12],
                  sheet[index][13],
                  sheet[index][14],
                  sheet[index][15])
    plants.append(plant)
    index += 1

dbname = "plant_db.pkl"
with open(dbname, "wb") as fout:
    pickle.dump(plants, fout)
