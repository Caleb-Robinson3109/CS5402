import wfdb
import wfdb.processing
import numpy as np
from scipy.signal import find_peaks
from scipy import stats
import os
import matplotlib.pyplot as plt
import csv
from scipy import stats
from scipy.stats import kurtosis, skew
from scipy.signal import periodogram
from scipy.integrate import trapezoid

def processSignalFiles(signalFilesToOpen, directory):
    recordData = np.array([])
    frequency = 0
    seenRecords = 0
    goalRecords = 0
    if len(signalFilesToOpen) == 0:
            print("no signal files found, skipping")
            return []
        
    for file in signalFilesToOpen:
        if goalRecords != 0 and seenRecords >= goalRecords:
            break
        IIindex = -1
        record = wfdb.rdrecord(directory + "/" + file[:-4])
        if IIindex == -1:
            if "II" not in record.sig_name:
                print("II not found, skipping")
                return []
            else:
                IIindex = record.sig_name.index("II")
                #print(record.sig_name)
            if frequency != 0:
                assert frequency == int(record.fs)
            frequency = int(record.fs)
            goalRecords = frequency * 3600
        if IIindex != -1:
            #print(record.p_signal.shape)
            min(1, 2)
            records_to_pull = min(goalRecords - seenRecords, record.p_signal.shape[0])
            recordData = np.concatenate((recordData, record.p_signal[:records_to_pull, IIindex]))
            seenRecords += records_to_pull

    #chop off initial nans/zeros
    #print(recordData.shape[0])
    #print(recordData[40000])
    cutOffPoint = 0
    for x in range((recordData.shape[0])):
        if recordData[x] != 0 and not np.isnan(recordData[x]):
            cutOffPoint = x
            break
    #print(cutOffPoint)

    recordData = recordData[cutOffPoint:]

    #chop off ending nans/zeros
    cutOffPoint = -1
    for x in range(1, (recordData.shape[0]) + 1):
        if recordData[-x] != 0 and not np.isnan(recordData[-x]):
            cutOffPoint = -x
            break
    if cutOffPoint != -1:
        recordData = recordData[:cutOffPoint+1]
        #print(cutOffPoint)


    if recordData.shape[0] == 0:
        print("no records found total, skipping patient")
        return []
    if recordData.shape[0] < frequency * 2700:
        print("not enough data found, skipping patient")
        print(recordData)
        return []
    
    #replace any intermediate zeros with a mean of its surrounding points
    for x in range(1, recordData.shape[0] - 1):
        if np.isnan(recordData[x]):
            if np.isnan(recordData[x+1]):
                recordData[x] = recordData[x-1]
            else:
                recordData[x] = (recordData[x-1] + recordData[x+1])/2

    #power appears to just be the sum of the squared signal values divded by the length
    power = np.nansum(recordData * recordData) / recordData.shape[0]
    _, psd = periodogram(recordData, frequency, scaling='spectrum')
    esd = trapezoid(psd)
    if np.isnan(esd):
        print(_)
        print(psd)
        exit()
    #plt.plot(recordData) #TODO preprocess the record data as needed and then return the averaged power and energy spectral density
    #plt.show()
    return [power, esd]
    



#get the list of alive and dead subject IDs

f = open("aliveSubjectIds.csv")
g = csv.reader(f)
next(g)
aliveList = []
for row in g:
    aliveList.append(row[0])
f.close()

f = open("deadSubjectIds.csv")
g = csv.reader(f)
next(g)
deadList = []
for row in g:
    deadList.append(row[0])
f.close()

#create output file
outputFile = open("CompiledData.csv", "w")
writer = csv.writer(outputFile)
writer.writerow(["subjectId", "Alive", "max", "min", "avg", "median", "mode", "std", "var", "range", "kurt", "skew", "avgPwr", "ESD"])

for (dirpath, dirnames, filenames) in os.walk("./"):
    
    dirSegs = dirpath.split("/")
    #print(dirSegs)
    if len(dirSegs) > 0 and len(dirSegs[-1]) == 7 and dirSegs[-1].startswith("p") and dirSegs[-1][1:].isdigit():
        directory = dirpath
    else:
        continue

    #import all the data files
    files = os.listdir(directory + "/")
    signalFilesToOpen = []
    digitalFileToOpen = ""
    for filename in files:
        if filename.split("-")[0].startswith("p"):
            subjectId = int(filename.split("-")[0][1:])
        if len(filename.split("_")) == 2 and filename.split("_")[1][:4].isnumeric() and filename.endswith("hea"):
            signalFilesToOpen.append(filename)
        elif len(filename.split("-")) == 6 and filename.endswith("n.hea"):
            digitalFileToOpen = filename[:-4]

    #print(filesToOpen)

    recordData = np.array([])
    
    #process the signal files
    temp = processSignalFiles(signalFilesToOpen, directory)
    avgPower = np.nan
    esd = np.nan #TODO change this back to nan after implementing raw signal processing
    if len(temp) != 0:
        avgPower = temp[0]
        esd = temp[1]
   
    #now process the digital file
    if digitalFileToOpen == "":
        print(f"No digital file found for subject {subjectId}, skipping")
        continue
    try:
        digData = wfdb.rdrecord(directory + "/" + digitalFileToOpen)
    except Exception as e:
        print("failed to open digital directory, there likely was not enough information and the downloader ignored it")
        print(e)
        continue
    if "HR" not in digData.sig_name:
        print(f"HR not found in data for subject {subjectId}, skipping")
        continue

    frequency = digData.fs

    if digData.p_signal.shape[0] < 2700 * frequency:
        print(f"Not enough HR data found for subject {subjectId}, skipping")
        continue
    heartRate = digData.p_signal[:int(frequency * 3600), digData.sig_name.index("HR")] 
    #print(len(heartRate))
    #print(heartRate)
    #remove leading zeros/nans
    cutOffPoint = 0
    for x in range((heartRate.shape[0])):
        if heartRate[x] != 0 and not np.isnan(heartRate[x]):
            cutOffPoint = x
            break
    heartRate = heartRate[cutOffPoint:]
    #print(len(heartRate))
    #remove outliers with a rolling window of 30 mins
    outlierWindow = int(round(frequency * 60 * 30))
    zscore = 3
    for x in range(heartRate.shape[0] - outlierWindow):
        mean = np.mean(heartRate[x:x+outlierWindow])
        std = np.std(heartRate[x:x+outlierWindow])
        maxArray = np.full((outlierWindow), zscore * std + mean)              
        minArray = np.full((outlierWindow), mean - zscore * std)             
        heartRate[x:x+outlierWindow] = np.maximum(heartRate[x:x+outlierWindow], minArray)
        heartRate[x:x+outlierWindow] = np.minimum(heartRate[x:x+outlierWindow], maxArray)

    #smooth signal willing window of size of 5 minutes
    windowSize = int(round(frequency * 60 * 5))
    if len(heartRate) < windowSize * 2 + 1:
        print("not enough data found for smoothing! skipping")
        #print(len(heartRate))
        #print(subjectId)
        continue
    #smoothedHeartRate = np.array(heartRate)
    #for x in range(1, windowSize):
    #    smoothedHeartRate += np.concatenate([heartRate[x+1:], np.zeros(x+1, dtype="int32")])
    #    smoothedHeartRate += np.concatenate([np.zeros(x+1, dtype="int32"), heartRate[:-(x+1)]])

    #smoothedHeartRate = smoothedHeartRate / ((windowSize-1)*2 + 1)
    #heartRate = smoothedHeartRate
    #calculate various metrics
    maxVal = np.max(heartRate)
    minVal = np.min(heartRate)
    avg = np.mean(heartRate)
    median = np.median(heartRate)
    mode = stats.mode(heartRate)[0][0]
    std = np.std(heartRate) 
    var = np.var(heartRate) 
    rangeVal = maxVal - minVal
    kurt = kurtosis(heartRate)
    sk = skew(heartRate)

    aliveStatus = 3

    if str(subjectId) in aliveList:
        aliveStatus = True
    elif str(subjectId) in deadList:
        aliveStatus = False
    if aliveStatus == 3:
        print("id not found in alive or dead list!")
        print(subjectId)
        print(aliveList)
        exit()

    writer.writerow([subjectId, aliveStatus, maxVal, minVal, avg, median, mode, std, var, rangeVal, kurt, sk, avgPower, esd])
    print(f"Successfully processed {subjectId}")

