# -*- coding: utf-8 -*-
"""label 4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/129WwgwpYyZDAFL8-h0U5LLC_ylVN86Cz
"""

# import libraries
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, mean_squared_error
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, KFold
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression

# read the test and train data files
train_df = pd.read_csv("train.csv")
valid_df = pd.read_csv("valid.csv")
test_df = pd.read_csv("test.csv")

train4_df = train_df.iloc[:,:]
valid4_df = valid_df.iloc[:, :]
test4_df = test_df.iloc[:, 1:]

train4_df.drop(columns=["label_1", "label_2", "label_3"], inplace=True)
valid4_df.drop(columns=["label_1", "label_2", "label_3"], inplace=True)

# splitting the test and train datasets into X and Y values
X4_train= train4_df.iloc[:,0:-1].values
Y4_train = train4_df.iloc[:,-1].values
X4_valid = valid4_df.iloc[:,0:-1].values
Y4_valid = valid4_df.iloc[:,-1].values
X4_test = test4_df.iloc[:,:].values

# scalling and fitting data
scaler = StandardScaler()
scaler.fit(X4_train)

X4_train = scaler.transform(X4_train)
X4_valid = scaler.transform(X4_valid)
X4_test = scaler.transform(X4_test)

classifiers = [
    ("Random Forest", RandomForestClassifier()),
    ("K-Nearest Neighbors", KNeighborsClassifier(n_neighbors=5)),
    ("Support Vector Machine", SVC(kernel="linear"))
]


# Iterate over each classifier and perform cross-validation
for clf_name, clf in classifiers:
    cross_val_scores = cross_val_score(clf, X4_train, Y4_train, cv=5)

    # Print the cross-validation scores for each classifier
    print(f"{clf_name} Cross-validation scores:", cross_val_scores)

    # Calculate and print the mean and standard deviation of the scores
    print(f"{clf_name} Mean accuracy:", cross_val_scores.mean())
    print(f"{clf_name} Standard deviation:", cross_val_scores.std())
    print("\n")

# Initialize and train a Support Vector Machine classifier
model =  RandomForestClassifier()
model.fit(X4_train, Y4_train)

# Make predictions on the test set
y_pred = model.predict(X4_valid)

print(classification_report(Y4_valid, y_pred))

train4_df['label_4'].value_counts().plot(kind='bar',title='Imbalanced data')

pip install imbalanced-learn

# resampling the data
from imblearn.combine import SMOTETomek

resampler = SMOTETomek(random_state=0)
X4_train, Y4_train = resampler.fit_resample(X4_train, Y4_train)

# Initialize and train a Support Vector Machine classifier
model.fit(X4_train, Y4_train)

# Make predictions on the test set
y_pred = model.predict(X4_valid)

print(classification_report(Y4_valid, y_pred))

# Create a SelectKBest instance with a scoring function (e.g., chi-squared)
selector = SelectKBest(score_func=f_classif, k=400)  # Select the top 2 features

# Fit and transform your data to select the best k features
X4_best_train = selector.fit_transform(X4_train, Y4_train)
X4_best_valid = selector.transform(X4_valid)
X4_best_test = selector.transform(X4_test)

model.fit(X4_best_train, Y4_train)

# Make predictions on the test set
y_pred = model.predict(X4_best_valid)

print(classification_report(Y4_valid, y_pred))

preds_before_PCA = model.predict(X4_best_test)
data_frame = pd.DataFrame(preds_before_PCA, columns=["label_4"])
data_frame.to_csv(f"190110V_4_1.csv",na_rep='')

pca=PCA(0.95)
pca = pca.fit(X4_best_train)

x4_train_pca=pca.fit_transform(X4_best_train)
x4_valid_pca = pca.transform(X4_best_valid)
x4_test_pca = pca.transform(X4_best_test)

model.fit(x4_train_pca, Y4_train)

# Make predictions on the test set
y_pred = model.predict(x4_valid_pca)

print(classification_report(Y4_valid, y_pred))

preds_after_PCA = model.predict(x4_test_pca)
data_frame = pd.DataFrame(preds_after_PCA, columns=["label_4"])
data_frame.to_csv(f"190110V_4_2.csv",na_rep='')

x4_train_pca.shape

param_grid = {
    'C': [0.001, 0.01, 0.1, 1, 10],     # Regularization parameter
    'penalty': ['l1', 'l2'],           # Regularization penalty ('l1' for L1 regularization, 'l2' for L2 regularization)
    'solver': ['liblinear', 'saga'],   # Algorithm to use in the optimization problem
}

# Create a GridSearchCV object with cross-validation
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', verbose=1, n_jobs=-1)

# Fit the GridSearchCV object to the data to find the best hyperparameters
grid_search.fit(x4_train_pca, Y4_train)

# Print the best hyperparameters and corresponding accuracy
best_params = grid_search.best_params_
best_accuracy = grid_search.best_score_
print("Best Hyperparameters:", best_params)
print("Best Accuracy:", best_accuracy)

best_model = grid_search.best_estimator_
y_pred = best_model.predict(x4_valid_pca)
test_preds = best_model.predict(x4_test_pca)

print(classification_report(Y1_valid, y_pred))

data_frame = pd.DataFrame(test_preds, columns=["label_4"])
data_frame.to_csv(f"190110V_4.csv",na_rep='')

