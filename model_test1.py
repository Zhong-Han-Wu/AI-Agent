import pandas as pd
from sklearn.tree import DecisionTreeClassifier
X = [[0.8, 1], [-0.5, 0], [0.9, 1], [-0.2, 0]] 
y = ["漲", "跌", "漲", "跌"]
clf=DecisionTreeClassifier()
clf.fit(X,y)
prediction=clf.predict([[0.7,1]])
print(f"根據訓練結果，AI 預測股價將會：{prediction[0]}")