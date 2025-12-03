const API_BASE = "http://localhost:8000";

let currentGoal = "";
let tasks = [];
let activeTaskIndex = -1;
let autoRunning = false;

const els = {
  status: document.getElementById("api-status"),
  goalInput: document.getElementById("goal-input"),
  planBtn: document.getElementById("plan-btn"),
  taskList: document.getElementById("task-list"),
  planCard: document.getElementById("plan-card"),
  activeTaskDetails: document.getElementById("active-task-details"),
  executeTaskBtn: document.getElementById("execute-task-btn"),
  autoRunBtn: document.getElementById("auto-run-btn"),
  finalReportCard: document.getElementById("final-report-card"),
  finalReport: document.getElementById("final-report"),
  memorySearchInput: document.getElementById("memory-search-input"),
  memorySearchBtn: document.getElementById("memory-search-btn"),
  memoryResults: document.getElementById("memory-results"),
  progressText: document.getElementById("progress-text"),
  taskSpinner: document.getElementById("task-spinner"),
  exportPdfBtn: document.getElementById("export-pdf-btn"),
};

window.addEventListener("beforeunload", (e) => {
  e.stopImmediatePropagation();
});

document.addEventListener("submit", (e) => e.preventDefault());
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter") e.preventDefault();   // block auto submit
});


// ---- Health check ----
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    els.status.textContent = res.ok ? "Backend: online" : "Backend: error";
    els.status.classList.add(res.ok ? "status-ok" : "status-error");
  } catch {
    els.status.textContent = "Backend: unreachable";
    els.status.classList.add("status-error");
  }
}
window.addEventListener("DOMContentLoaded", checkHealth);

// ---- Generate Plan ----
els.planBtn.addEventListener("click", async () => {
  const goal = els.goalInput.value.trim();
  if (!goal) return alert("Please enter a research goal.");

  currentGoal = goal;
  els.finalReportCard.style.display = "none";
  els.finalReport.textContent = "";
  autoRunning = false;

  els.activeTaskDetails.innerHTML = "<p>Planning...</p>";
  els.progressText.textContent = "Planning tasks...";
  els.taskSpinner.classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });

    const data = await res.json();
    tasks = data.map(t => ({ ...t, status: "PENDING", findings: "", sources: [] }));

    els.planCard.style.display = "block";
    renderTaskList();
    setActiveTask(0);
    els.executeTaskBtn.disabled = false;
    els.autoRunBtn.disabled = false;
    els.progressText.textContent = `Plan ready — ${tasks.length} tasks generated.`;
  } catch {
    alert("Plan generation failed");
  } finally {
    els.taskSpinner.classList.add("hidden");
  }
});

// ---- Render Task List ----
function renderTaskList() {
  els.taskList.innerHTML = "";
  tasks.forEach((task, idx) => {
    const li = document.createElement("li");
    li.className = "task-item" + (idx === activeTaskIndex ? " active" : "");
    li.dataset.index = idx;

    li.innerHTML = `<span>${task.title}</span>
                    <span class="task-status">${task.status}</span>`;

    li.style.cursor = "pointer";
    li.addEventListener("click", () => {
      if (!autoRunning) setActiveTask(idx);
    });

    els.taskList.appendChild(li);
  });
}

// ---- Set Active Task ----
function setActiveTask(index) {
  activeTaskIndex = index;
  renderTaskList();
  const task = tasks[index];
  els.activeTaskDetails.innerHTML = `
    <h3>${task.title}</h3>
    <p><strong>Description:</strong> ${task.description}</p>
    <p><strong>Search query:</strong> ${task.search_query || "(none)"}</p>
    <p><strong>Status:</strong> ${task.status}</p>
    <h4>Findings</h4>
    <pre>${task.findings || "Not executed yet."}</pre>
    ${renderSources(task.sources)}
  `;
  els.executeTaskBtn.disabled = false;
}

function renderSources(sources) {
  if (!sources?.length) return "<p><em>No sources recorded.</em></p>";
  return `
    <h4>Sources</h4>
    <ul>
      ${sources
      .map(
        s => `<li><a href="${s.url}" target="_blank">${s.title || s.url}</a><br/><small>${s.snippet || ""}</small></li>`
      )
      .join("")}
    </ul>
  `;
}

// ---- Execute Single Task ----
els.executeTaskBtn.addEventListener("click", async () => {
  if (activeTaskIndex >= 0) await runTask(activeTaskIndex);
});

async function runTask(index) {
  const task = tasks[index];
  tasks[index].status = "IN_PROGRESS";
  setActiveTask(index);
  els.progressText.textContent = `Executing ${index + 1}/${tasks.length}...`;
  els.taskSpinner.classList.remove("hidden");

  try {
    const context = tasks.filter(t => t.findings).map(t => t.findings).join("\n\n");

    const res = await fetch(`${API_BASE}/execute_task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task, context }),
    });

    const data = await res.json();
    tasks[index].status = "COMPLETED";
    tasks[index].findings = data.findings;
    tasks[index].sources = data.sources || [];
    setActiveTask(index);
  } catch {
    tasks[index].status = "FAILED";
  } finally {
    els.taskSpinner.classList.add("hidden");
  }
}

// ---- Auto Run ----
els.autoRunBtn.addEventListener("click", async () => {
  if (!tasks.length) return;

  autoRunning = !autoRunning;
  els.autoRunBtn.textContent = autoRunning ? "Stop Auto Run" : "Run All Tasks (Auto)";

  if (!autoRunning) return;

  for (let i = 0; i < tasks.length; i++) {
    if (!autoRunning) break;
    if (tasks[i].status === "COMPLETED") continue;

    await runTask(i);

    // prevent refresh during auto sequence
    history.pushState(null, "", window.location.href);

    await new Promise(resolve => setTimeout(resolve, 200));
  }


  autoRunning = false;
  els.autoRunBtn.textContent = "Run All Tasks (Auto)";
  await finalReportIfDone();
});

// ---- Final Report ----
async function finalReportIfDone() {
  if (!tasks.every(t => t.status === "COMPLETED")) return;

  els.progressText.textContent = "Generating final report...";
  els.taskSpinner.classList.remove("hidden");

  const res = await fetch(`${API_BASE}/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      goal: currentGoal,
      tasks_with_findings: tasks.map(t => ({
        id: t.id,
        title: t.title,
        description: t.description,
        findings: t.findings,
      })),
    }),
  });

  const data = await res.json();
  els.finalReport.textContent = data.report;
  els.finalReportCard.style.display = "block";
  els.progressText.textContent = "Final report ready.";
  els.taskSpinner.classList.add("hidden");
}

// ---- Export PDF ----
els.exportPdfBtn.addEventListener("click", () => {
  const win = window.open("", "_blank");
  win.document.write(`<pre>${els.finalReport.textContent}</pre>`);
  win.print();
});

// ---- Memory Search ----
els.memorySearchBtn.addEventListener("click", async () => {
  const q = els.memorySearchInput.value.trim();
  if (!q) return alert("Enter query");

  const res = await fetch(`${API_BASE}/memory/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: q, k: 10 }),
  });

  const data = await res.json();
  renderMemory(data.results);
});

function renderMemory(results) {
  els.memoryResults.innerHTML = results
    .map(
      r => `<div class="memory-item">
        <div>${(r.content || "").slice(0, 200)}...</div>
        <div class="memory-tags">${r.metadata?.tags || ""}</div>
      </div>`
    )
    
    .join("");
}
