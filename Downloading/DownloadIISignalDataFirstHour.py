import csv
import os
import time

def sortRecords(x):
    f = x.split("-")[1:]
    #p004807-2122-09-01-09-12.hea
    return int(f[0]) * 100000000 + int(f[1]) * 1000000 + int(f[2]) * 10000 + int(f[3]) * 100 + int(f[4])


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
        if f"p{fullNumber}" in line and line[-1] != "n": 
            metaRecords.append(line)
            if line[-1] == "\n":
                raise Exception("Caught newline when opening records file")
            #metaRecords.append(line.split("-")[1:])
    recordsFile.close()

    #metarecords now contains the dates of the files in yyyy, mm, dd, hh, MM format, find the one that is the earliest and open that associated metadata file
    #for each field starting from the left, if the top two results match, then we move to the next field until we run out of fields. If we run out of fields, exit with an error
    if len(metaRecords) == 0:
        print(f"No metadata records found for subject id {subjectId}, skipping")
        time.sleep(5)
        continue

    metaRecords.sort(key=sortRecords)
    print("sorted meta records:")
    print(metaRecords)

    #download record header
    print(f"downloading header file {metaRecords[0]}")
    p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{metaRecords[0]}.hea")
    if p != 0:
        raise Exception(f"Failed to download metarecord file {metaRecords[0]} for patient {subjectId}")

    metaFile = open(f"physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{metaRecords[0]}.hea")
    headerLine = metaFile.readline().split(" ")
    freq = int(headerLine[2])
    requiredSamples = freq * 3600 #required samples for one hour of data

    totalSamples = int(headerLine[3])
    if requiredSamples > totalSamples+1: #small leeway 
        print(f"not enough sample data for {subjectId}. Required {requiredSamples}, only detected {totalSamples}, skipping")
        metaFile.close()
        time.sleep(5)
        continue

    #now that we know enough samples are present, download the first file (the layout file) to verify that II records are present
    layoutFile = metaFile.readline().split(" ")[0]
    assert(layoutFile.endswith("layout"))
    p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{layoutFile}.hea")
    if p != 0:
        raise Exception(f"Failed to download layout file {layoutFile} for patient {subjectId}")
    
    layoutFile = open(f"physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{layoutFile}.hea")
    
    #to check for II, just check if II is detected on any line
    readingDetected = False
    for line in layoutFile.readlines():
        if "II" in line:
            readingDetected = True
    
    layoutFile.close()
    if not readingDetected:
        print(f"II reading not detected for subject {subjectId}, skipping")
        metaFile.close()
        time.sleep(5)
        continue

    # now that we know the II measurement is preesent, download actual files until we reach the desired number of samples
    downloadedSamples = 0
    #first, we will acquire files to download until we reach the desired number of samples
    filesToDownload = []
    for line in metaFile.readlines():
        content = line.split(" ")
        if content[0] != "~": #records skipped
            filesToDownload.append(content[0])
        downloadedSamples += int(content[1])
        if downloadedSamples >= requiredSamples:
            break

    metaFile.close()
    #now, download all the necessary files and headers
    print(f"About to download {len(filesToDownload)} sample files for subject {subjectId}: {filesToDownload}")

    for file in filesToDownload:
        p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{file}.hea")
        if p != 0:
            raise Exception(f"Failed to download file {file} for patient {subjectId}")
        
        p = os.system(f"wget -r -N -c -np https://physionet.org/files/mimic3wdb-matched/1.0/p{firstTwo}/p{fullNumber}/{file}.dat")
        if p != 0:
            raise Exception(f"Failed to download file {file} for patient {subjectId}")
        
    print(f"Successfully downloaded all necessary files for {subjectId}, continuing")

        








    


f.close()
g.close()