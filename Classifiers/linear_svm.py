import pandas as pd
import numpy as np
from sklearn.svm import LinearSVC  # import both
from smote_variants import A_SUWO
import CrossValidation

# Get our kfoldcv iterator
dataIterator = iter(CrossValidation.KFoldCV(10))

for p in dataIterator:
    if type(StopIteration) == type(p):
        break
    trainX, trainY, testX, testY = p

    print("Started Iteration")
    # Standardize predictors
    maxes = []
    mins = []
    for col in range(trainX.shape[1]):
        mins.append(min(trainX[:, col]))
        maxes.append(max(trainX[:, col]))
        if maxes[col] != mins[col]:  # Prevent division by zero
            trainX[:, col] = (trainX[:, col] - mins[col]) / (maxes[col] - mins[col])
            testX[:, col] = (testX[:, col] - mins[col]) / (maxes[col] - mins[col])
        else:
            trainX[:, col] = 0
            testX[:, col] = 0

    # Apply A_SUWO oversampling to the training set to handle imbalanced data
    trainX, trainY = A_SUWO().sample(trainX, trainY)

    # Build and Fit Classifier
    model = LinearSVC(max_iter=10000)
    model.fit(trainX, trainY)

    # Predict on classifier with testX
    y_pred = model.predict(testX)

    # Add metrics
    dataIterator.storePredictions(testY, y_pred)
    print("Finished Iteration")

# Print final metrics
dataIterator.calculateMetrics()
