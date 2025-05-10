import pandas as pd
import numpy as np
import CrossValidation

print("Baseline model that always 'predicts' true")
#get our kfoldcv iterator
dataIterator = iter(CrossValidation.KFoldCV(10))


for p in dataIterator:
    if type(StopIteration) == type(p):
        break
    trainX, trainY, testX, testY = p
    y_pred = np.array([1] * testY.shape[0])

    dataIterator.storePredictions(testY, y_pred)
    print("Finished Iteration")

dataIterator.calculateMetrics()


print("Baseline model that always 'predicts' false")
#get our kfoldcv iterator
dataIterator = iter(CrossValidation.KFoldCV(10))

for p in dataIterator:
    if type(StopIteration) == type(p):
        break
    trainX, trainY, testX, testY = p
    y_pred = np.array([-1] * testY.shape[0])

    dataIterator.storePredictions(testY, y_pred)
    print("Finished Iteration")

dataIterator.calculateMetrics()