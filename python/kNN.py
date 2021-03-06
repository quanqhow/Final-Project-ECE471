from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import sys
import performance

class kNNClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, k_value=1, minkowski_p=2):
        self.k_value = k_value
        self.minkowski_p = minkowski_p

    def fit(self, X, y):
        self.data_ = np.array(X)
        self.class_ = np.array(y)
        return self

    def _minkowski_distance(self,u,v):
        if self.minkowski_p == np.inf:
            return float(max(np.abs(u-v)))
        else:
            return sum(abs(u-v)**(float(self.minkowski_p))) ** (1/float(self.minkowski_p))

    def _predict_isntance(self, point,k):
        #find the closest classes
        distance_list = []
        for i in range(0,len(self.data_)):
            distance_list.append(self._minkowski_distance(point[:],self.data_[i]))
        neighbor_points = sorted(zip(distance_list,self.class_),key=lambda distance_list: distance_list[0])[:k]

        #Decide the closest class
        neighbor_votes = {}
        while(len(neighbor_points)>0):
            for neighbor in neighbor_points:
                try:
                    neighbor_votes[int(neighbor[-1])]+= 1
                except KeyError:
                    neighbor_votes[int(neighbor[-1])] = 1

            class_options   = list(neighbor_votes.keys())
            class_votes     = list(neighbor_votes.values())
            predicted_class = np.where(class_votes == np.array(class_votes).max())[0]

            #remove the furtherest away point and repeat voting
            if len(predicted_class) > 1:
                del neighbor_points[-1]
            else:
                return class_options[predicted_class[0]]
        else:
            print("No neighbors were found")
            sys.exit()

    #predict all
    def predict(self, X):
        try:
            getattr(self, "data_")
        except AttributeError:
            raise RuntimeError("Fit the classifier before using it")

        return([self._predict_isntance(x,self.k_value) for x in X])

    def score(self, X, y):
        predicted_X = self.predict(X)
        return accuracy_score(predicted_X,y)

def run(X_train,y_train,X_test,y_test,predciction_filename=None,graph_name=None):

    #Find the best parameters using GridSearchCV -- SPECIFY param_grid
    param_grid = {
                    'n_neighbors':[5,10,20,40],
                    'p':[1,2,3,np.inf]
                 }
    gs = GridSearchCV(KNeighborsClassifier(), param_grid,cv=4,n_jobs=-1)
    gs.fit(X_train,y_train)
    predicted_classes = gs.best_estimator_.predict(X_test)

    if graph_name != None:
        performance.plot_roc(gs,X_test,y_test,graph_name)

    return performance.get_scores(gs.best_params_,predicted_classes,y_test,predciction_filename)
