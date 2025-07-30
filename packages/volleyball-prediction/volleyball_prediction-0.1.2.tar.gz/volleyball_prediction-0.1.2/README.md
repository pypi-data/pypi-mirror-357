# volleyball_prediction
This Python package contains a machine learning model to predict the outcome of women's volleyball matches. The model can also be provided as a REST API with FastAPI.

---

## Features

- Prediction of international matches (example: Türkiye vs. Serbia)
- Ready-trained model (recorded with joblib)
- Get live predictions via API
- Data cleaning and preprocessing with Pandas

---

## Installation

You can install it from PyPI with the following command:

```bash
pip install volleyball_prediction


from volleyball_prediction.main import guess

print(guess("Türkiye", "Sırbistan"))
# Output: "Türkiye" veya "Sırbistan"

uvicorn volleyball_prediction.predict_api:app --reload

---

