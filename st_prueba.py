import streamlit as st
from sklearn import datasets
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

st.title("Título de proyecto final")

dataset_name=st.sidebar.selectbox("Selecciona un dataset", ["Iris", "Breast cancer", "Wine"])

st.write(dataset_name)

classifier_name=st.sidebar.selectbox("Selecciona un clasificador", ["KNN", "SVM", "Random Forest"])

def get_dataset(dataset_name):
    if dataset_name=="Iris":
        data=datasets.load_iris()
    elif dataset_name=="Breast cancer":
        data=datasets.load_breast_cancer()
    else:
        data=datasets.load_wine()
    X=data.data
    y=data.target
    return X, y

X, y=get_dataset(dataset_name)
st.write("Shape of dataset", X.shape)
st.write("Numero de clases", len(np.unique(y)))


def parameters_ui(clf_name):
    params= dict()
    if clf_name=="KNN":
        K=st.sidebar.slider("K", 1, 15)
        params["K"]=K
    elif clf_name=="SVM":
        C=st.sidebar.slider("C", 0.01, 10.0)
        params["C"]=C
    else:
        max_depth=st.sidebar.slider("max_depth", 2, 15)
        n_estimators=st.sidebar.slider("n_estimators", 1, 100)
        params["max_depth"]=max_depth
        params["n_estimators"]=n_estimators
    return params

add_parameters=parameters_ui(classifier_name)

def get_classifier(clf_name, params):
    if clf_name=="KNN":
        clf=KNeighborsClassifier(n_neighbors=params["K"])
    elif clf_name=="SVM":
        clf=SVC(C=params["C"])
    else:
        clf=RandomForestClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], random_state=1234)
    return clf

clf=get_classifier(classifier_name, add_parameters)

#Clasificación
x_train, x_test, y_train, y_test=train_test_split(X, y, test_size=0.2, random_state=1234)

clf.fit(x_train, y_train)
y_pred=clf.predict(x_test)

acc=accuracy_score(y_test, y_pred)

st.write(f"Clasificador: {classifier_name}")
st.write(f"Precisión: {acc}")


#Plot
pca=PCA(2)
X_projected=pca.fit_transform(X)

X1=X_projected[:, 0]
X2=X_projected[:, 1]

fig = plt.figure()
plt.scatter(X1, X2, c=y, alpha=0.8, cmap="viridis")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.colorbar()

st.pyplot(fig)