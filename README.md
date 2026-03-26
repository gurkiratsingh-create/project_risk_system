# 🚀 Real-Time Project Risk & Delay Prediction System

An AI-powered analytics dashboard that predicts project delays and provides real-time risk insights for project managers.

---

## 📌 Overview

The **Real-Time Project Risk & Delay Prediction System** is a full-stack machine learning application designed to help project managers:

* Predict project delay risks using ML
* Monitor portfolio health in real time
* Analyze trends and performance
* Make data-driven decisions

This system combines **machine learning + analytics dashboard + modern UI** to simulate a real SaaS product.

---

## 🧠 Key Features

### 🔐 Authentication System

* User Registration & Login
* Secure password hashing using Flask-Bcrypt
* Session management using Flask-Login
* Per-user project data isolation

---

### 🤖 Machine Learning Prediction

* Random Forest model (scikit-learn)
* Predicts:

  * Delay probability
  * Risk score (0–100%)
* REST API endpoint: `/predict`

---

### 📊 Interactive Dashboard

#### KPI Metrics

* Total Projects
* Projects at Risk
* On Track Projects
* Average Risk Score

#### 🎯 Live Risk Gauge

* Displays real-time risk of latest analyzed project
* Animated gauge with status indicator

#### 🧠 Manager Insights

* AI-style portfolio insights
* Highlights:

  * High-risk projects
  * Medium-risk alerts
  * Portfolio health summary
  * Latest project analysis

#### 📈 Risk Trend Chart

* Time-based trend visualization
* Smooth curve with gradient fill
* Built using Chart.js

#### 📁 Project Overview

* Displays recent projects
* Risk badges and timestamps
* Scrollable list

---

### 📑 Analytics & Reporting

#### 📊 Portfolio Performance Report

* Total projects
* Delayed vs on-track
* Average risk
* Risk range

#### 🍩 Risk Distribution Chart

* Doughnut chart showing:

  * Low / Medium / High risk projects

#### 🔥 Risk Heatmap

* Visual bar representation of project risks

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Login
* Flask-Bcrypt

### Machine Learning

* scikit-learn (Random Forest)
* pandas
* joblib

### Frontend

* HTML5
* CSS3 (Glassmorphism UI)
* JavaScript (Vanilla JS)

### Visualization

* Chart.js

### Database

* SQLite

---

## 📁 Project Structure

```
project_risk_system/

│── app.py
│── risk_model.pkl
│── database.db
│
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│
├── static/
│   ├── style.css
│   ├── script.js
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/project-risk-system.git
cd project-risk-system
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run the Application

```bash
python app.py
```

---

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 🔄 API Endpoints

### POST `/predict`

Predict project risk

**Request Body:**

```json
{
  "name": "Project A",
  "progress": 50,
  "deadline": 30,
  "budget": 60,
  "team": 5
}
```

**Response:**

```json
{
  "risk": 72.5,
  "status": "Delayed"
}
```

---

### GET `/history`

Returns all user projects

---

## 🎯 How It Works

1. User inputs project details
2. Frontend sends request to `/predict`
3. ML model calculates:

   * Risk probability
   * Delay classification
4. Backend stores project in database
5. Dashboard updates in real time:

   * Gauge
   * Insights
   * Charts
   * Project list

---

## 🧩 Core Logic

### Risk Calculation Features

* Task completion rate
* Budget burn rate
* Team productivity
* Historical delay rate

---

## 🎨 UI/UX Highlights

* Glassmorphism design
* Animated components
* Responsive layout
* Real-time updates
* Clean analytics structure

---

## 🚀 Future Improvements

* Role-based access (Admin / User)
* Real-time updates with WebSockets
* Export reports (PDF/CSV)
* ML model improvements (XGBoost, Neural Nets)
* Project filters and sorting
* Notifications & alerts
* Deployment on cloud (AWS / Render / Vercel)

---

## 📌 Use Cases

* Project Management
* Agile Sprint Monitoring
* Startup Product Teams
* Portfolio Risk Analysis
* Academic ML Projects

---

## 🤝 Contribution

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Gurkirat Singh Bhangoo**
Built as a full-stack ML + dashboard system for real-world project analytics.

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!
