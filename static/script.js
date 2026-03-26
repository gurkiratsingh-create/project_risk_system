let chart;
let chartData = [];
let chartLabels = [];
let projects = [];
let firstHistory = true;
let riskChart;
// ===============================
// LOAD HISTORY FROM DATABASE
// ===============================
window.onload = async function () {

    try {

        const response = await fetch("/history");
        const data = await response.json();

        projects = [];
        chartData = [];
        chartLabels = [];

        data.forEach((project) => {

            project.riskClass =
                project.status === "Delayed" ? "high" :
                project.risk > 40 ? "medium" : "low";

            projects.push(project);
            chartData.push(project.risk);
            chartLabels.push(project.name);

            if (document.getElementById("historyBody")) {
                addHistoryRow(project);
            }

        });

        // UPDATE GAUGE + INSIGHTS WITH MOST RECENT PROJECT
        if (projects.length > 0) {

            const latest = projects[projects.length - 1];

            if (document.getElementById("gaugeFill"))
                updateGauge(latest.risk, latest.riskClass, latest.name);

            if (document.getElementById("insights"))
                generateInsights();
        }

        if (document.getElementById("projects"))
            renderProjectList();

        if (document.getElementById("chart"))
            updateChart();

        if (document.getElementById("kpi-total"))
            updateKPI();

    } catch (error) {
        console.error("Error loading history:", error);
    }

};

// ===============================
// ADD PROJECT (REAL ML CALL)
// ===============================
async function addProject() {

    const name = document.getElementById("name").value.trim();
    const progress = parseFloat(document.getElementById("progress").value);
    const deadline = parseFloat(document.getElementById("deadline").value);
    const budget = parseFloat(document.getElementById("budget").value);
    const team = parseFloat(document.getElementById("team").value);

    if (!name || isNaN(deadline) || isNaN(team)) {
        showToast("⚠️ Please fill required fields.");
        return;
    }

    const btn = document.getElementById("analyzeBtn");
    btn.classList.add("loading");

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name,
                progress: progress,
                deadline: deadline,
                budget: budget,
                team: team
            })
        });

        const data = await response.json();
        btn.classList.remove("loading");

        const risk = data.risk;
        const status = data.status;

        const riskClass =
            status === "Delayed" ? "high" :
            risk > 40 ? "medium" : "low";

        const project = {
            name,
            risk,
            status,
            riskClass,
            timestamp: new Date().toLocaleString()
        };

        projects.unshift(project);

        updateGauge(risk, riskClass,name);
        renderProjectList();
        updateKPI();
        generateInsights();
        addHistoryRow(project);

        chartData.push(risk);
        chartLabels.push(name);

        if(chartData.length > 10){
        chartData.shift();
        chartLabels.shift();
    }

updateChart();

        clearForm();

    } catch (error) {
        btn.classList.remove("loading");
        showToast("🚨 Backend error. Is Flask running?");
        console.error(error);
    }
}
function toggleDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

document.addEventListener('click', function(event) {
    const profile = document.querySelector('.profile');
    const dropdown = document.getElementById('profileDropdown');
    
    if (profile && !profile.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

window.addEventListener('scroll', function() {
    const nav = document.querySelector('.top-nav');
    if (window.pageYOffset > 10) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});
// ===============================
// ENHANCED MANAGER INSIGHTS
// ===============================
function generateInsights(){

    const container = document.getElementById("insights");
    if(!container) return;

    container.innerHTML = "";

    if(projects.length === 0){
        container.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">💡</div>
            <p>No insights available yet.</p>
        </div>`;
        return;
    }

    const highRisk = projects.filter(p => p.risk >= 70);
    const mediumRisk = projects.filter(p => p.risk >= 40 && p.risk < 70);
    const lowRisk = projects.filter(p => p.risk < 40);

    const latest = projects[projects.length - 1];

    /* ---------- HIGH RISK ALERT ---------- */

    if(highRisk.length > 0){

        const p = highRisk[0];

        container.innerHTML += `
        <div class="insight-box critical">
            <div class="insight-icon">🚨</div>
            <div>
                <div class="insight-title">Critical Project Risk</div>
                <div class="insight-text">
                <b>${p.name}</b> has a delay risk of <b>${p.risk}%</b>.
                <br>
                Recommendation: Increase team capacity or extend deadlines.
                </div>
            </div>
        </div>`;
    }

    /* ---------- MEDIUM RISK ---------- */

    if(mediumRisk.length > 0){

        container.innerHTML += `
        <div class="insight-box warning">
            <div class="insight-icon">⚠️</div>
            <div>
                <div class="insight-title">Projects Require Monitoring</div>
                <div class="insight-text">
                ${mediumRisk.length} project(s) have moderate risk.
                <br>
                Recommendation: Review budget burn and sprint velocity.
                </div>
            </div>
        </div>`;
    }

    /* ---------- PORTFOLIO HEALTH ---------- */

    if(lowRisk.length > 0){

        container.innerHTML += `
        <div class="insight-box healthy">
            <div class="insight-icon">✅</div>
            <div>
                <div class="insight-title">Portfolio Health Stable</div>
                <div class="insight-text">
                ${lowRisk.length} project(s) are currently on track.
                Maintain current execution strategy.
                </div>
            </div>
        </div>`;
    }

    /* ---------- LATEST PROJECT ---------- */

    if(latest){

        container.innerHTML += `
        <div class="insight-box">
            <div class="insight-icon">📌</div>
            <div>
                <div class="insight-title">Latest Project Analysis</div>
                <div class="insight-text">
                Most recent analysis: <b>${latest.name}</b>
                <br>
                Risk Score: <b>${latest.risk}%</b> (${latest.status})
                </div>
            </div>
        </div>`;
    }

}
// ===============================
// CLEAR FORM
// ===============================
function clearForm() {
    document.getElementById("name").value = "";
    document.getElementById("deadline").value = "";
    document.getElementById("team").value = "";
    document.getElementById("progress").value = 50;
    document.getElementById("budget").value = 50;
    document.getElementById("progressVal").textContent = "50%";
    document.getElementById("budgetVal").textContent = "50%";
}

// ===============================
// GAUGE
// ===============================
// ===============================
// ENHANCED GAUGE ANIMATION
// ===============================
function updateGauge(risk, riskClass,projectName) {

    const fill = document.getElementById("gaugeFill");
    const number = document.getElementById("gaugeNumber");
    const pill = document.getElementById("statusPill");

    if (!fill || !number || !pill) return;

    const arcLen = 251;

    // Smooth animated arc
    const targetOffset = arcLen - (risk / 100) * arcLen;
    fill.style.transition = "stroke-dashoffset 1.5s cubic-bezier(0.22,1,0.36,1)";
    fill.style.strokeDashoffset = targetOffset;

    const colors = {
        low: "#68d391",
        medium: "#f6ad55",
        high: "#fc8181"
    };

    fill.style.stroke = colors[riskClass];
    const projectLabel = document.getElementById("gaugeProjectName");

if(projectLabel && projectName){
    projectLabel.textContent = "Project: " + projectName;
}

    // 🔥 Animated number counter
    let start = 0;
    const duration = 1200;
    const startTime = performance.now();

    function animateNumber(currentTime) {
        const progress = Math.min((currentTime - startTime) / duration, 1);
        const value = Math.floor(progress * risk);
        number.textContent = value + "%";
        number.setAttribute("fill", colors[riskClass]);

        if (progress < 1) {
            requestAnimationFrame(animateNumber);
        }
    }

    requestAnimationFrame(animateNumber);

    // Status pill animation
    pill.style.transform = "scale(0.8)";
    pill.style.opacity = "0";

    setTimeout(() => {
        pill.textContent =
            riskClass === "high" ? "🚨 Delayed" :
            riskClass === "medium" ? "⚠️ Monitor Closely" :
            "✅ On Track";

        pill.style.transition = "all 0.4s ease";
        pill.style.transform = "scale(1)";
        pill.style.opacity = "1";
    }, 300);
}

// ===============================
// PROJECT LIST
// ===============================
function renderProjectList() {

    const container = document.getElementById("projects");

    if (!container) return;
    container.innerHTML = "";

if(projects.length === 0){
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📋</div>
            <p>No projects analyzed yet.<br>Add your first project above.</p>
        </div>
    `;
    return;
}

    projects.forEach(p => {
        const div = document.createElement("div");
        div.className = `project-item ${p.riskClass}`;
        div.innerHTML = `
            <div>
                <div class="project-name">${p.name}</div>
                <div class="project-meta">${p.timestamp}</div>
            </div>
            <div class="risk-badge">${p.risk}%</div>
        `;
        container.appendChild(div);
    });
}
// ===============================
// REPORT
// ===============================
function generateReport() {
    const reportCard = document.getElementById("reportCard");

if (!reportCard) return;

    if (projects.length === 0) {
        showToast("⚠️ No projects to report yet.");
        return;
    }

    const total = projects.length;
    const delayed = projects.filter(p => p.status === "Delayed").length;
    const low = projects.filter(p => p.risk < 40).length;
    const medium = projects.filter(p => p.risk >= 40 && p.risk < 70).length;
    const high = projects.filter(p => p.risk >= 70).length;
    const avgRisk = (projects.reduce((s, p) => s + p.risk, 0) / total).toFixed(1);
    const maxRisk = Math.max(...projects.map(p => p.risk));
    const minRisk = Math.min(...projects.map(p => p.risk));

    document.getElementById("reportCard").style.display = "block";

    document.getElementById("report").innerHTML = `
<div class="report-item">
    <div class="report-item-label">Total Projects</div>
    <div class="report-item-value">${total}</div>
</div>

<div class="report-item">
    <div class="report-item-label">Delayed Projects</div>
    <div class="report-item-value" style="color:#fc8181">${delayed}</div>
</div>

<div class="report-item">
    <div class="report-item-label">On Track</div>
    <div class="report-item-value" style="color:#68d391">${total - delayed}</div>
</div>

<div class="report-item">
    <div class="report-item-label">Average Risk</div>
    <div class="report-item-value">${avgRisk}%</div>
</div>

<div class="report-item">
    <div class="report-item-label">Highest Risk</div>
    <div class="report-item-value">${maxRisk}%</div>
</div>

<div class="report-item">
    <div class="report-item-label">Risk Range</div>
    <div class="report-item-value">${minRisk}% – ${maxRisk}%</div>
</div>
`;

    document.getElementById("reportCard").scrollIntoView({ behavior: "smooth" });
    const ctx = document.getElementById("riskDistributionChart").getContext("2d");

if (riskChart) {
    riskChart.destroy();
}

riskChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        labels: ["Low Risk", "Medium Risk", "High Risk"],
        datasets: [{
            data: [low, medium, high],
            backgroundColor: [
                "#68d391",
                "#f6ad55",
                "#fc8181"
            ],
            borderWidth: 0,
            cutout: "70%"
        }]
    },
   options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
            legend: {
                labels: {
                    color: "#fff"
                }
            }
        }
    }
});
const heatmapContainer = document.getElementById("riskHeatmap");

heatmapContainer.innerHTML = "";

projects.forEach(project => {

    const row = document.createElement("div");
    row.className = "heatmap-row";

    const riskClass =
        project.risk >= 70 ? "risk-high" :
        project.risk >= 40 ? "risk-medium" :
        "risk-low";

    row.innerHTML = `
        <div class="heatmap-label">${project.name}</div>

        <div class="heatmap-bar">
            <div class="heatmap-fill ${riskClass}" style="width:${project.risk}%"></div>
        </div>

        <div class="heatmap-percent">${project.risk}%</div>
    `;

    heatmapContainer.appendChild(row);

});
}

// ===============================
// KPI
// ===============================
function updateKPI() {

    if (!document.getElementById("kpi-total")) return;
    const total = projects.length;
    const delayed = projects.filter(p => p.status === "Delayed").length;
    const onTrack = total - delayed;

    const avgRisk = total > 0
        ? (projects.reduce((sum, p) => sum + p.risk, 0) / total).toFixed(0)
        : 0;

    document.getElementById("kpi-total").textContent = total;
    document.getElementById("kpi-delayed").textContent = delayed;
    document.getElementById("kpi-ontrack").textContent = onTrack;
    document.getElementById("kpi-avgrisk").textContent = avgRisk + "%";
}

// ===============================
// HISTORY
// ===============================
   function addHistoryRow(project) {

    const tbody = document.getElementById("historyBody");

    if (!tbody) return;

    if (firstHistory) {
        tbody.innerHTML = "";
        firstHistory = false;
    }

    const row = document.createElement("tr");

    row.innerHTML = `
        <td>${project.name}</td>
        <td>${project.risk}%</td>
        <td>${project.status}</td>
        <td>${project.timestamp}</td>
    `;

    tbody.insertBefore(row, tbody.firstChild);
}

// ===============================
// CHART
// ===============================
function updateChart(){

    const canvas = document.getElementById("chart");
    if(!canvas) return;

    const ctx = canvas.getContext("2d");

    const gradient = ctx.createLinearGradient(0,0,0,400);
    gradient.addColorStop(0,"rgba(99,179,237,0.45)");
    gradient.addColorStop(1,"rgba(99,179,237,0.02)");

    if(!chart){

        chart = new Chart(ctx,{
            type:"line",
            data:{
                labels: chartLabels,
                datasets:[{
                    label:"Risk %",
                    data: chartData,

                    borderColor:"#63b3ed",
                    backgroundColor: gradient,
                    fill:true,

                    tension:0.45,

                    pointRadius:5,
                    pointHoverRadius:7,
                    pointBackgroundColor:"#63b3ed",
                    pointBorderColor:"#0f172a",
                    pointBorderWidth:2,

                    borderWidth:3
                }]
            },

            options:{
                responsive:true,
                maintainAspectRatio:false,   // ⭐ important fix

                plugins:{
                    legend:{
                        labels:{
                            color:"#cbd5e1",
                            font:{ size:12 }
                        }
                    },

                    tooltip:{
                        backgroundColor:"#111827",
                        borderColor:"#63b3ed",
                        borderWidth:1,
                        titleColor:"#fff",
                        bodyColor:"#cbd5e1",
                        padding:10
                    }
                },

                scales:{

                    x:{
                        ticks:{
                            color:"#94a3b8",
                            maxRotation:0,
                            autoSkip:true,
                            maxTicksLimit:8
                        },
                        grid:{
                            display:false
                        }
                    },

                    y:{
                        beginAtZero:true,
                        max:100,
                        ticks:{
                            color:"#94a3b8"
                        },
                        grid:{
                            color:"rgba(255,255,255,0.04)"
                        }
                    }
                }
            }
        });

    }else{

        chart.data.labels = chartLabels;
        chart.data.datasets[0].data = chartData;
        chart.update();

    }
}

// ===============================
// TOAST
// ===============================
function showToast(message){

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `
        <span>${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">×</span>
    `;

    document.body.appendChild(toast);

    setTimeout(()=>{
        toast.remove();
    },3000);
}
/* ================================================
   SETTINGS PAGE — Interactive JS
   Add this to your existing script.js
   ================================================ */

// -----------------------------------------------
// 1. PROFILE FORM — Save to Flask backend
// -----------------------------------------------
function saveProfile() {
    const data = {
        first_name:   document.querySelector('input[placeholder="First name"]')?.value,
        last_name:    document.querySelector('input[placeholder="Last name"]')?.value,
        email:        document.querySelector('input[type="email"]')?.value,
        role:         document.querySelector('input[placeholder="e.g. Project Manager"]')?.value,
        organisation: document.querySelector('input[placeholder="Company name"]')?.value,
        bio:          document.querySelector('textarea')?.value,
    };

    fetch('/api/settings/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            showSaved('profileSaved');
            // Update navbar username live
            document.querySelectorAll('.profile-name, .dropdown-user-name')
                .forEach(el => el.textContent = data.first_name || el.textContent);
        } else {
            alert('Error saving profile: ' + (res.error || 'Unknown error'));
        }
    })
    .catch(err => console.error('Profile save error:', err));
}

// -----------------------------------------------
// 2. PASSWORD CHANGE — Post to Flask
// -----------------------------------------------
function updatePassword() {
    const current  = document.querySelector('input[placeholder="Enter current password"]')?.value;
    const newPwd   = document.getElementById('newPwd')?.value;
    const confirm  = document.querySelector('input[placeholder="Repeat new password"]')?.value;

    if (!current || !newPwd || !confirm) {
        alert('Please fill in all password fields.');
        return;
    }
    if (newPwd !== confirm) {
        alert('New passwords do not match.');
        return;
    }
    if (newPwd.length < 8) {
        alert('Password must be at least 8 characters.');
        return;
    }

    fetch('/api/settings/password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: current, new_password: newPwd })
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            showSaved('pwdSaved');
            // Clear all password fields
            document.querySelectorAll('#panel-security input[type="password"]')
                .forEach(el => el.value = '');
            document.getElementById('strengthWrap').style.display = 'none';
        } else {
            alert('Error: ' + (res.error || 'Current password is incorrect'));
        }
    })
    .catch(err => console.error('Password update error:', err));
}

// -----------------------------------------------
// 3. NOTIFICATIONS — Save all toggle states
// -----------------------------------------------
function saveNotifications() {
    // Collect every toggle on the notifications panel
    const toggles = {};
    document.querySelectorAll('#panel-notifications .s-toggle').forEach((toggle, i) => {
        toggles[`notif_${i}`] = toggle.checked;
    });

    // Give each toggle a meaningful name using its sibling h4
    const named = {};
    document.querySelectorAll('#panel-notifications .s-notif-item').forEach(item => {
        const label  = item.querySelector('h4')?.textContent?.trim()
                            .toLowerCase().replace(/\s+/g, '_').replace(/[^a-z_]/g, '');
        const checked = item.querySelector('.s-toggle')?.checked;
        if (label) named[label] = checked;
    });

    fetch('/api/settings/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(named)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) showSaved('notifSaved');
        else alert('Error saving notifications: ' + (res.error || ''));
    })
    .catch(err => console.error('Notifications save error:', err));
}

// -----------------------------------------------
// 4. APPEARANCE — Save theme preferences
// -----------------------------------------------
function saveAppearance() {
    const darkMode       = document.getElementById('darkToggle')?.checked;
    const reducedMotion  = document.querySelectorAll('#panel-appearance .s-toggle')[1]?.checked;
    const fontSize       = document.querySelector('#panel-appearance .s-select')?.value;
    const language       = document.querySelectorAll('#panel-appearance .s-select')[1]?.value;
    const accentColour   = document.querySelector('.s-color-swatch.selected')?.title || 'Aurora';

    const prefs = { dark_mode: darkMode, reduced_motion: reducedMotion,
                    font_size: fontSize, language, accent_colour: accentColour };

    // Apply immediately in the browser
    document.body.classList.toggle('dark-theme', darkMode);
    if (reducedMotion) {
        document.body.style.setProperty('--transition-base', '0.01ms');
    } else {
        document.body.style.removeProperty('--transition-base');
    }

    fetch('/api/settings/appearance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prefs)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) showSaved('appearanceSaved');
        else alert('Error: ' + (res.error || ''));
    })
    .catch(err => console.error('Appearance save error:', err));
}

// -----------------------------------------------
// 5. SESSION REVOKE — Call backend
// -----------------------------------------------
function revokeSession(sessionId, btn) {
    if (!confirm('Revoke this session? That device will be signed out.')) return;

    btn.textContent = '...';
    btn.disabled    = true;

    fetch('/api/settings/sessions/revoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            const row = btn.closest('.s-session');
            row.style.transition = 'opacity .4s, transform .4s';
            row.style.opacity    = '0';
            row.style.transform  = 'translateX(20px)';
            setTimeout(() => row.remove(), 400);
        } else {
            btn.textContent = 'Revoke';
            btn.disabled    = false;
            alert('Error: ' + (res.error || ''));
        }
    })
    .catch(err => {
        btn.textContent = 'Revoke';
        btn.disabled    = false;
        console.error('Session revoke error:', err);
    });
}

function revokeAllSessions() {
    if (!confirm('Sign out all other devices? You will stay signed in here.')) return;

    fetch('/api/settings/sessions/revoke-all', { method: 'POST' })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            // Remove all non-current session rows
            document.querySelectorAll('.s-session').forEach(row => {
                if (!row.innerHTML.includes('Current session')) {
                    row.style.transition = 'opacity .4s';
                    row.style.opacity    = '0';
                    setTimeout(() => row.remove(), 400);
                }
            });
        }
    })
    .catch(err => console.error('Revoke all error:', err));
}

// -----------------------------------------------
// 6. API KEY — Generate via backend
// -----------------------------------------------
function generateKey() {
    fetch('/api/settings/apikeys/generate', { method: 'POST' })
    .then(r => r.json())
    .then(res => {
        if (!res.key) { alert('Error generating key'); return; }

        const k    = res.key;
        const list = document.getElementById('apiKeyList');
        const div  = document.createElement('div');
        div.className = 's-api-key';
        div.style.animation = 'popIn .4s cubic-bezier(.34,1.56,.64,1) both';
        div.innerHTML = `
            <div style="font-size:12px;font-weight:700;color:#6366f1;min-width:70px">New Key</div>
            <div class="s-api-key-val">${k.substring(0, 12)}••••••••••••••••••••••</div>
            <button class="s-btn s-btn-ghost s-btn-sm"
                    onclick="copyKey(this,'${k}')">Copy</button>
            <button class="s-btn s-btn-danger s-btn-sm"
                    onclick="revokeApiKey('${res.key_id}', this)">Revoke</button>`;
        list.prepend(div);
    })
    .catch(err => console.error('Key generate error:', err));
}

function revokeApiKey(keyId, btn) {
    if (!confirm('Permanently revoke this API key?')) return;

    fetch('/api/settings/apikeys/revoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key_id: keyId })
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            const row = btn.closest('.s-api-key');
            row.style.transition = 'opacity .3s';
            row.style.opacity    = '0';
            setTimeout(() => row.remove(), 300);
        } else {
            alert('Error: ' + (res.error || ''));
        }
    });
}

// -----------------------------------------------
// 7. AVATAR UPLOAD — Send image to backend
// -----------------------------------------------
document.getElementById('avatarInput')?.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { alert('File is too large. Max 5MB.'); return; }

    const formData = new FormData();
    formData.append('avatar', file);

    // Preview immediately in browser
    const reader = new FileReader();
    reader.onload = e => {
        const inner = document.querySelector('.s-avatar-inner');
        if (inner) {
            inner.style.backgroundImage = `url(${e.target.result})`;
            inner.style.backgroundSize  = 'cover';
            inner.textContent           = '';
        }
    };
    reader.readAsDataURL(file);

    fetch('/api/settings/avatar', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(res => {
        if (res.success) showSaved('profileSaved');
        else alert('Upload failed: ' + (res.error || ''));
    })
    .catch(err => console.error('Avatar upload error:', err));
});

// -----------------------------------------------
// 8. LOAD SAVED SETTINGS — On page load
// -----------------------------------------------
function loadSettings() {
    fetch('/api/settings/load')
    .then(r => r.json())
    .then(data => {
        // Profile
        if (data.first_name)
            document.querySelector('input[placeholder="First name"]').value = data.first_name;
        if (data.last_name)
            document.querySelector('input[placeholder="Last name"]').value = data.last_name;
        if (data.role)
            document.querySelector('input[placeholder="e.g. Project Manager"]').value = data.role;
        if (data.organisation)
            document.querySelector('input[placeholder="Company name"]').value = data.organisation;
        if (data.bio)
            document.querySelector('textarea').value = data.bio;

        // Appearance
        if (data.dark_mode) {
            document.getElementById('darkToggle').checked = true;
            document.body.classList.add('dark-theme');
        }

        // Notifications — match by index
        if (data.notifications) {
            const keys    = Object.keys(data.notifications);
            const toggles = document.querySelectorAll('#panel-notifications .s-toggle');
            keys.forEach((key, i) => {
                if (toggles[i]) toggles[i].checked = data.notifications[key];
            });
        }
    })
    .catch(err => console.error('Settings load error:', err));
}

// Run on page load if we're on the settings page
if (document.getElementById('panel-profile')) {
    loadSettings();
}