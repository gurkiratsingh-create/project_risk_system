<h1 align="center">🚀 RiskPulse — Real-Time Project Risk & Delay Prediction System</h1>

<p align="center">
  <a href="https://riskpulse-ygtv.onrender.com"><b>🌐 Live Demo</b></a>
</p>

<p align="center">
  <i>AI-powered full-stack SaaS for predicting project risks and delays</i>
</p>

<hr>

<h2>📌 Overview</h2>

<p>
The <b>Real-Time Project Risk & Delay Prediction System</b> is a full-stack machine learning application designed to help project managers:
</p>

<ul>
<li>Predict project delay risks using ML</li>
<li>Monitor portfolio health in real time</li>
<li>Analyze trends and performance</li>
<li>Make data-driven decisions</li>
</ul>

<p>
This system combines <b>machine learning + analytics dashboard + modern UI</b> to simulate a real SaaS product.
</p>

<hr>

<h2>🧠 Key Features</h2>

<h3>🔐 Authentication System</h3>
<ul>
<li>User Registration & Login</li>
<li>Secure password hashing using Flask-Bcrypt</li>
<li>Session management using Flask-Login</li>
<li>Per-user project data isolation</li>
</ul>

---

<h3>🤖 Machine Learning Prediction</h3>
<ul>
<li>Random Forest model (scikit-learn)</li>
<li>Predicts:
  <ul>
    <li>Delay probability</li>
    <li>Risk score (0–100%)</li>
  </ul>
</li>
<li>Custom feature engineering pipeline</li>
<li>REST API endpoint: <code>/predict</code></li>
</ul>

---

<h3>📊 Interactive Dashboard</h3>

<b>KPI Metrics</b>
<ul>
<li>Total Projects</li>
<li>Projects at Risk</li>
<li>On Track Projects</li>
<li>Average Risk Score</li>
</ul>

<b>🎯 Live Risk Gauge</b>
<ul>
<li>Displays real-time risk of latest analyzed project</li>
<li>Animated gauge with status indicator</li>
</ul>

<b>🧠 Manager Insights</b>
<ul>
<li>AI-style portfolio insights</li>
<li>Highlights:
  <ul>
    <li>High-risk projects</li>
    <li>Medium-risk alerts</li>
    <li>Portfolio health summary</li>
    <li>Latest project analysis</li>
  </ul>
</li>
</ul>

<b>📈 Risk Trend Chart</b>
<ul>
<li>Time-based trend visualization</li>
<li>Smooth curve with gradient fill</li>
<li>Built using Chart.js</li>
</ul>

<b>📁 Project Overview</b>
<ul>
<li>Displays recent projects</li>
<li>Risk badges and timestamps</li>
<li>Scrollable list</li>
</ul>

---

<h3>📑 Analytics & Reporting</h3>

<b>📊 Portfolio Performance Report</b>
<ul>
<li>Total projects</li>
<li>Delayed vs on-track</li>
<li>Average risk</li>
<li>Risk range</li>
</ul>

<b>🍩 Risk Distribution Chart</b>
<ul>
<li>Doughnut chart showing:
  <ul>
    <li>Low / Medium / High risk projects</li>
  </ul>
</li>
</ul>

<b>🔥 Risk Heatmap</b>
<ul>
<li>Visual bar representation of project risks</li>
</ul>

<hr>

<h2>⚙️ Backend Engineering Enhancements (Added)</h2>

<ul>
<li>Rate limiting (Flask-Limiter)</li>
<li>Structured logging system</li>
<li>Secure API architecture</li>
<li>Input validation & error handling</li>
<li>Production-ready Gunicorn setup</li>
<li>Environment-based configuration</li>
</ul>

<hr>

<h2>🛠️ Tech Stack</h2>

<h3>Backend</h3>
<ul>
<li>Python</li>
<li>Flask</li>
<li>Flask-SQLAlchemy</li>
<li>Flask-Login</li>
<li>Flask-Bcrypt</li>
<li>Flask-Migrate</li>
<li>Flask-Limiter</li>
</ul>

<h3>Machine Learning</h3>
<ul>
<li>scikit-learn (Random Forest)</li>
<li>NumPy</li>
<li>Joblib</li>
<li>Custom feature engineering</li>
</ul>

<h3>Frontend</h3>
<ul>
<li>HTML5</li>
<li>CSS3 (Glassmorphism UI)</li>
<li>JavaScript (Vanilla JS)</li>
</ul>

<h3>Visualization</h3>
<ul>
<li>Chart.js</li>
</ul>

<h3>Database</h3>
<ul>
<li>PostgreSQL (Production - Render)</li>
<li>SQLite (Development)</li>
</ul>

<h3>Deployment</h3>
<ul>
<li>Render (Cloud Hosting)</li>
<li>Gunicorn</li>
</ul>

<hr>

<h2>📁 Project Structure</h2>

<pre>
project_risk_system/

│── app.py
│── risk_model.pkl
│
├── templates/
├── static/
├── logs/
</pre>

<hr>

<h2>⚙️ Installation & Setup</h2>

<pre>
git clone https://github.com/your-username/project-risk-system.git
cd project-risk-system
</pre>

<pre>
python -m venv venv
source venv/bin/activate
</pre>

<pre>
pip install -r requirements.txt
</pre>

<pre>
python app.py
</pre>

<hr>

<h2>🔄 API Endpoints</h2>

<h3>POST /predict</h3>

<pre>
{
  "name": "Project A",
  "progress": 50,
  "deadline": 30,
  "budget": 60,
  "team": 5
}
</pre>

<pre>
{
  "risk": 72.5,
  "status": "Delayed"
}
</pre>

<h3>GET /history</h3>
<p>Returns all user projects</p>

<hr>

<h2>🧠 How It Works</h2>

<ol>
<li>User inputs project details</li>
<li>Frontend sends request to backend</li>
<li>Feature engineering is applied</li>
<li>ML model predicts risk</li>
<li>Data stored in database</li>
<li>Dashboard updates in real time</li>
</ol>

<hr>

<h2>🎨 UI/UX Highlights</h2>

<ul>
<li>Glassmorphism design</li>
<li>Responsive layout</li>
<li>Animated components</li>
<li>Clean SaaS dashboard UI</li>
</ul>

<hr>

<h2>🚀 Live Deployment</h2>

<p>
🔗 <a href="https://riskpulse-ygtv.onrender.com">https://riskpulse-ygtv.onrender.com</a>
</p>

<hr>

<h2>📈 What Makes This Project Strong</h2>

<ul>
<li>End-to-end ML system (not just model)</li>
<li>Full-stack architecture</li>
<li>Production deployment experience</li>
<li>Real-world problem solving</li>
<li>Scalable backend design</li>
</ul>

<hr>

<h2>🚧 Future Improvements</h2>

<ul>
<li>Advanced explainability (SHAP)</li>
<li>Model versioning</li>
<li>API monetization</li>
<li>Real-time updates (WebSockets)</li>
</ul>

<hr>

<h2>👨‍💻 Author</h2>

<p><b>Gurkirat Singh Bhangoo</b></p>

<p>
Built as a flagship full-stack AI product demonstrating real-world ML system design.
</p>

<hr>

<h2 align="center">⭐ Star this repo if you like it!</h2>