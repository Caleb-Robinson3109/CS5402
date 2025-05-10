import csv
deathSet = set()
#Get list of subject IDS who have died
f = open("ADMISSIONS.csv")
reader = csv.reader(f)
print(next(reader)[1])
for row in reader:
    if row[5] == "":
        deathSet.add(row[1])
f.close()

#Get list of subject IDs who ended in the CCU
ccuSet = set()
f = open("ICUSTAYS.csv")
reader = csv.reader(f)
print(next(reader)[1])
for row in reader:
    if row[6] == "CCU":
        ccuSet.add(row[1])
f.close()

#combine list
finalSet = set()

for id in ccuSet:
    if id in deathSet:
        finalSet.add(id)

#output final set to file
f = open("passedSubjectIds.csv", "w")
f.write("SUBECT_ID\n")
for id in finalSet:
    f.write(id)
    f.write("\n")
f.close