# RandomForest

# 0. import libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from sklearn.datasets import load_breast_cancer

# 1. data
dataset=load_breast_cancer()

x_train, x_test, y_train, y_test=train_test_split(
        dataset.data, dataset.target, train_size=0.8, random_state=23
)

x_train=x_train[:, [0,2,3]]
x_test=x_test[:, [0,2,3]]

# 2. model
model=RandomForestClassifier()

# 3. fitting
model.fit(x_train, y_train)

# 4. score, predict
acc=model.score(x_test, y_test)

print('acc : ', acc)

def plot_feature_importances(model):
    n_features=dataset.data.shape[1]
    plt.barh(np.arange(n_features), model.feature_importances_,
        align='center') # bar 형태의 그래프
    plt.yticks(np.arange(n_features), dataset.feature_names)
    plt.xlabel('Feature Importances')
    plt.ylabel('Features')
    plt.ylim(-1, n_features)

plot_feature_importances(model)
plt.show()

# results
# [0.09649293 0.02822648 0.4012841  0.47399649]
# acc :  0.9666666666666667

# [0.20461069 0.35917997 0.43620934]
# acc :  1.0

'''
def cut_columns(feature_importances,columns,number):
    temp = []
    for i in feature_importances:
        temp.append(i)
    temp.sort()
    temp=temp[:number]
    result = []
    for j in temp:
        index = feature_importances.tolist().index(j)
        result.append(columns[index])
    return result

print(cut_columns(model.feature_importances_,datasets.feature_names,8))

- 수현님 코드
'''