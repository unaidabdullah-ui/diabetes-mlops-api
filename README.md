![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![ML](https://img.shields.io/badge/Model-ScikitLearn-orange)

# 🩺 Diabetes Prediction API – MLOps Project (FastAPI + Docker)

🚀 A production-ready Machine Learning API built using FastAPI, Docker.
This project demonstrates a complete MLOps pipeline — from model training to deployment.

---

## 📌 Project Overview

This project predicts whether a person is diabetic based on health parameters using a Random Forest Classifier trained on the Pima Indians Diabetes Dataset.

---

## 📊 Problem Statement

Predict diabetes based on the following inputs:

- Pregnancies  
- Glucose  
- Blood Pressure  
- BMI  
- Age  

---

## 🧠 Tech Stack

- Machine Learning: Scikit-learn  
- Backend: FastAPI  
- Containerization: Docker   
- Language: Python  
- Model Serialization: Joblib  

---

## ⚙️ Features

- ML Model Training  
- REST API using FastAPI  
- Dockerized Application  
- Scalable & Production-ready Structure  

---

## 📁 Project Structure

Diabetes_project/

├── main.py                  
├── train.py                 
├── diabetes_model.pkl      
├── requirements.txt          
├── Dockerfile              
└── README.md                

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

git clone https://github.com/unaidabdullah-ui/diabetes-mlops-api.git
cd diabetes-mlops-project  

---

### 2️⃣ Create Virtual Environment

python3 -m venv .mlops  
source .mlops/bin/activate  

---

### 3️⃣ Install Dependencies

pip install -r requirements.txt  

---

## 🏋️ Train the Model

python train.py  

---

## 🚀 Run the API Locally

uvicorn main:app --reload  

Open: http://127.0.0.1:8000/docs  

---

## 📥 Sample API Request

POST /predict

{
  "Pregnancies": 2,
  "Glucose": 130,
  "BloodPressure": 70,
  "BMI": 28.5,
  "Age": 45
}

---

## 🐳 Docker Setup

Build Docker Image:

docker build -t diabetes-mlops .  

Run Container:

docker run -p 8000:8000 diabetes-mlops  


## 📈 Future Improvements

- Add CI/CD pipeline (GitHub Actions / Jenkins)  
- Model versioning with MLflow / DVC  
- Monitoring with Prometheus & Grafana  
- Cloud deployment (AWS / GCP)  

---

## 🙌 Author

Unaid Abdullah  
Aspiring MLOps Engineer | Full Stack Developer  

---

## ⭐ Show Your Support

If you found this project helpful:
- Star this repo  
- Fork it  
- Share with others  

---

## 📢 Credits

Inspired by MLOps tutorials and real-world deployment practices.
