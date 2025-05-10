import csv
import os
import time

def sortRecords(x):
    f = x.split("-")[1:]
    #p004807-2122-09-01-09-12.hea
    return int(f[0]) * 100000000 + int(f[1]) * 1000000 + int(f[2]) * 10000 + int(f[3]) * 100 + int(f[4][:-1])


splitNumber = input("Choose split number: ")
fileName = f"subjectIdsSplit{splitNumber}.csv"

f = open(fileName)
subjectIds = csv.reader(f)

g = open(f"outputSubjectIdsSplit{splitNumber}.csv", "w")

g.write(next(f)[0])
g.write("\n")

restartId = input("Choose id to restart at: ").zfill(6)
if restartId == "000000":
    skip = False
else:
    skip = True

for subjectId in subjectIds:
    
    fullNumber = str(subjectId[0]).zfill(6)
    firstTwo = fullNumber[:2]
    
    if restartId == fullNumber:
        skip = False
    if skip: continue

    #first, download the RECORDS file to see which records are available
    p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/RECORDS")
    if p != 0:
        print(f"Records file for subjectId {subjectId} not found, assuming subject doesnt exist in matched subset")
        g.write(fullNumber)
        g.write("\n")
        time.sleep(.5)
        continue

    recordsFile = open(f"physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/RECORDS")
    #now, we need to interpret the lines that start with p as dates and choose the file that has the lower date
    metaRecords = []
    for line in recordsFile.readlines():
        line = line[:-1] if line[-1] == "\n" else line
        if f"p{fullNumber}" in line and line[-1] == "n": 
            metaRecords.append(line)
            if line[-1] == "\n":
                raise Exception("Caught newline when opening records file")
            #metaRecords.append(line.split("-")[1:])
    recordsFile.close()

    #metarecords now contains the dates of the files in yyyy, mm, dd, hh, MM format, find the one that is the earliest and open that associated metadata file
    #for each field starting from the left, if the top two results match, then we move to the next field until we run out of fields. If we run out of fields, exit with an error
    if len(metaRecords) == 0:
        print("No metadata records found for subject id {subjectId}, skipping")
        time.sleep(5)
        continue

    metaRecords.sort(key=sortRecords)
    print("sorted meta records:")
    #print(metaRecords)

    #download record header
    #we download the latest one because we want the most recent ECU visit
    print(f"downloading header file {metaRecords[-1]}")
    p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{metaRecords[-1]}.hea")
    if p != 0:
        raise Exception(f"Failed to download metarecord file {metaRecords[-1]} for patient {subjectId}")

    metaFile = open(f"physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{metaRecords[-1]}.hea")
    headerLine = metaFile.readline().split(" ")
    freq = float(headerLine[2].split("/")[0])
    requiredSamples = int(freq * 3600) #required samples for one hour of data

    totalSamples = int(headerLine[3])
    if requiredSamples > totalSamples:
        print(f"not enough sample data for {subjectId}. Required {requiredSamples}, only detected {totalSamples}, skipping")
        metaFile.close()
        time.sleep(5)
        continue

    #now that we know enough samples are present, download the dat file and assume HR will be present, we will enforce this later on
    dataFile = metaFile.readline().split(" ")[0]
    assert(dataFile.endswith("n.dat"))
    p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{dataFile}")
    if p != 0:
        raise Exception(f"Failed to download layout file {dataFile} for patient {subjectId}")

    metaFile.close()
        
    print(f"Successfully downloaded all necessary files for {subjectId}, continuing")

        
f.close()
g.close()