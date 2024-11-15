import csv
import os
data = list()

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "2_monkey_traj.csv"
abs_file_path = os.path.join(script_dir, rel_path)
f = open(abs_file_path,'r')
rea = csv.reader(f)
for row in rea:
    data.append(row)

print(data)
f.close