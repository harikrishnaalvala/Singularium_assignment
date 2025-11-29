const state = {
    tasks: [],
    sequence: 1,
};

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content && meta.content !== "NOTPROVIDED") {
        return meta.content;
    }
    const name = "csrftoken=";
    const cookies = document.cookie ? document.cookie.split("; ") : [];
    for (const cookie of cookies) {
        if (cookie.startsWith(name)) {
            return decodeURIComponent(cookie.slice(name.length));
        }
    }
    return "";
}

function buildJsonHeaders() {
    return {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
    };
}

const elements = {
    year: document.getElementById("year"),
    form: document.getElementById("task-form"),
    inputs: {
        title: document.getElementById("task-title"),
        dueDate: document.getElementById("task-due-date"),
        hours: document.getElementById("task-hours"),
        importance: document.getElementById("task-importance"),
        dependencies: document.getElementById("task-dependencies"),
    },
    bulkJson: document.getElementById("bulk-json"),
    loadJson: document.getElementById("load-json"),
    clearTasks: document.getElementById("clear-tasks"),
    strategy: document.getElementById("strategy-select"),
    analyzeBtn: document.getElementById("analyze-btn"),
    suggestBtn: document.getElementById("suggest-btn"),
    suggestCount: document.getElementById("suggest-count"),
    taskTableBody: document.querySelector("#task-table tbody"),
    taskCount: document.getElementById("task-count"),
    priorityList: document.getElementById("priority-list"),
    blockedList: document.getElementById("blocked-list"),
    attentionList: document.getElementById("attention-list"),
    configView: document.getElementById("config-used"),
    suggestionsList: document.getElementById("suggestions-list"),
    messages: document.getElementById("messages"),
};

elements.year.textContent = new Date().getFullYear();

elements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    const task = buildTaskFromInputs();
    if (!task) {
        return;
    }
    state.tasks.push(task);
    state.sequence += 1;
    renderTasks();
    elements.form.reset();
});

elements.loadJson.addEventListener("click", () => {
    if (!elements.bulkJson.value.trim()) {
        showMessage("Paste JSON before loading.", "error");
        return;
    }
    try {
        const parsed = JSON.parse(elements.bulkJson.value);
        if (!Array.isArray(parsed)) {
            throw new Error("JSON must be an array of task objects.");
        }
        state.tasks = parsed.map((raw, index) => normalizeTask(raw, index + 1));
        state.sequence = state.tasks.length + 1;
        renderTasks();
        showMessage(`Loaded ${state.tasks.length} tasks from JSON.`, "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
});

elements.clearTasks.addEventListener("click", () => {
    state.tasks = [];
    state.sequence = 1;
    renderTasks();
    showMessage("Task list cleared.", "info");
});

elements.analyzeBtn.addEventListener("click", () => analyzeTasks());
elements.suggestBtn.addEventListener("click", () => fetchSuggestions());

elements.taskTableBody.addEventListener("click", (event) => {
    if (event.target.matches(".remove-task")) {
        const id = event.target.getAttribute("data-id");
        state.tasks = state.tasks.filter((task) => String(task.id) !== id);
        renderTasks();
    }
});

function buildTaskFromInputs() {
    const title = elements.inputs.title.value.trim();
    const dueDate = elements.inputs.dueDate.value;
    const hours = Number(elements.inputs.hours.value);
    const importance = Number(elements.inputs.importance.value);
    const dependencies = elements.inputs.dependencies.value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);

    if (!title || !dueDate || Number.isNaN(hours) || hours <= 0 || Number.isNaN(importance)) {
        showMessage("Please complete all fields with valid values.", "error");
        return null;
    }

    return {
        id: `task-${state.sequence}`,
        title,
        due_date: dueDate,
        estimated_hours: hours,
        importance,
        dependencies,
    };
}

function normalizeTask(raw, fallbackIndex) {
    return {
        id: raw.id || raw.task_id || `task-${fallbackIndex}`,
        title: raw.title || "Untitled Task",
        due_date: raw.due_date || new Date().toISOString().split("T")[0],
        estimated_hours: Number(raw.estimated_hours ?? 1) || 1,
        importance: Number(raw.importance ?? 1) || 1,
        dependencies: Array.isArray(raw.dependencies)
            ? raw.dependencies.map(String)
            : [],
    };
}

function renderTasks() {
    elements.taskTableBody.innerHTML = "";

    state.tasks.forEach((task) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${task.id || ""}</td>
            <td>${task.title}</td>
            <td>${task.due_date}</td>
            <td>${task.estimated_hours}</td>
            <td>${task.importance}</td>
            <td>${task.dependencies.join(", ")}</td>
            <td><button class="remove-task" data-id="${task.id}">Remove</button></td>
        `;
        elements.taskTableBody.appendChild(row);
    });

    elements.taskCount.textContent = `${state.tasks.length} ${state.tasks.length === 1 ? "task" : "tasks"}`;
}

function showMessage(text, type = "info") {
    elements.messages.innerHTML = `<div class="message ${type}">${text}</div>`;
}

function getStrategyOverrides() {
    const strategy = elements.strategy.value;
    switch (strategy) {
        case "fastest_wins":
            return { weight_effort: 2.5, weight_importance: 1.0, weight_urgency: 1.0 };
        case "high_impact":
            return { weight_importance: 3.0, weight_effort: 0.5, weight_urgency: 1.5 };
        case "deadline_driven":
            return { weight_urgency: 3.0, urgency_mode: "threshold", urgency_threshold: 2 };
        case "smart_balance":
        default:
            return {};
    }
}

async function analyzeTasks() {
    if (!state.tasks.length) {
        showMessage("Add some tasks before analyzing.", "error");
        return;
    }

    showMessage("Analyzing tasks…", "info");

    const payload = {
        tasks: state.tasks,
        config: getStrategyOverrides(),
    };

    try {
        const response = await fetch("/api/tasks/analyze/", {
            method: "POST",
            headers: buildJsonHeaders(),
            credentials: "same-origin",
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`Analyze failed (${response.status})`);
        }

        const data = await response.json();
        renderAnalysis(data.results);
        showMessage("Analysis ready.", "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function fetchSuggestions() {
    const topN = Number(elements.suggestCount.value) || 3;

    try {
        if (state.tasks.length) {
            await fetch("/api/tasks/suggest/", {
                method: "POST",
                headers: buildJsonHeaders(),
                credentials: "same-origin",
                body: JSON.stringify({ tasks: state.tasks }),
            });
        }

        const response = await fetch(`/api/tasks/suggest/?top_n=${topN}`);
        if (!response.ok) {
            throw new Error(`Suggest failed (${response.status})`);
        }

        const data = await response.json();
        renderSuggestions(data.results || []);
        showMessage("Suggestions refreshed.", "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderAnalysis(results) {
    renderResultList(elements.priorityList, results.priority_list, true);
    renderResultList(elements.blockedList, results.blocked_tasks);
    renderResultList(elements.attentionList, results.needs_attention);
    elements.configView.textContent = JSON.stringify(results.config_used, null, 2);
    renderSuggestions([]);
}

function renderResultList(target, items, decorate = false) {
    target.innerHTML = "";

    if (!items || !items.length) {
        const empty = document.createElement("li");
        empty.className = "result-card";
        empty.textContent = "No entries.";
        target.appendChild(empty);
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.classList.add("result-card");

        if (decorate) {
            const tier = classifyScore(item.score);
            li.classList.add(tier);
        }

        li.innerHTML = `
            <div><strong>${item.title || item.id}</strong></div>
            <div class="meta">Due: ${item.due_date || "n/a"} • Importance: ${item.importance ?? "-"} • Hours: ${item.estimated_hours ?? "-"}</div>
            <div class="score">Score: ${typeof item.score === "number" ? item.score.toFixed(2) : "n/a"}</div>
            <div class="reason">${item.explanation || ""}</div>
        `;

        if (item.blocked) {
            li.classList.add("blocked");
        }

        target.appendChild(li);
    });
}

function renderSuggestions(items) {
    elements.suggestionsList.innerHTML = "";

    if (!items || !items.length) {
        const empty = document.createElement("li");
        empty.className = "result-card";
        empty.textContent = "No suggestions yet.";
        elements.suggestionsList.appendChild(empty);
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.classList.add("result-card", classifyScore(item.score));
        li.innerHTML = `
            <div><strong>${item.title}</strong> <span class="score">(${item.score?.toFixed?.(2) ?? "n/a"})</span></div>
            <div class="meta">Due: ${item.due_date} • Importance: ${item.importance ?? "-"} • Hours: ${item.estimated_hours ?? "-"}</div>
            <div class="reason">${item.reason || ""}</div>
            <div class="meta">Status: ${item.status || "ok"}</div>
        `;
        elements.suggestionsList.appendChild(li);
    });
}

function classifyScore(score) {
    if (typeof score !== "number") {
        return "medium";
    }
    if (score >= 8) {
        return "high";
    }
    if (score >= 4) {
        return "medium";
    }
    return "low";
}

renderTasks();
showMessage("Load tasks and choose a strategy to begin.", "info");
