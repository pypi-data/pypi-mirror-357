import pickle

# Modeli yükle
with open("volley_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_result(X):
    """
    X: girdi verisi (özellikler)
    """
    return model.predict([X])[0]
