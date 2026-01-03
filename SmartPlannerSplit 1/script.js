
document.addEventListener("DOMContentLoaded", () => {
  const currentUser = localStorage.getItem("currentUser");
  if (!currentUser) {
    window.location.href = "login.html";
    return;
  }

  const avatar = document.getElementById("user-avatar");
  const displayName = document.getElementById("user-display");

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/*";
  fileInput.style.display = "none";
  fileInput.addEventListener("change", handleAvatarUpload);
  document.body.appendChild(fileInput);

  avatar.addEventListener("click", () => fileInput.click());

  function getUserData() {
    const users = JSON.parse(localStorage.getItem("users") || "{}");
    return users[currentUser];
  }

  function saveUserData(data) {
    const users = JSON.parse(localStorage.getItem("users") || "{}");
    users[currentUser] = data;
    localStorage.setItem("users", JSON.stringify(users));
  }

  const userData = getUserData();
  displayName.innerText = currentUser;

  if (userData.avatar) {
    avatar.style.backgroundImage = `url('${userData.avatar}')`;
    avatar.style.backgroundSize = "cover";
    avatar.innerText = "";
  } else {
    avatar.innerText = currentUser[0].toUpperCase();
    avatar.style.backgroundColor = stringToColor(currentUser);
  }

  function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
    return "#" + "00000".substring(0, 6 - c.length) + c;
  }

  function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function (e) {
      const user = getUserData();
      user.avatar = e.target.result;
      saveUserData(user);
      avatar.style.backgroundImage = `url('${e.target.result}')`;
      avatar.style.backgroundSize = "cover";
      avatar.innerText = "";
    };
    reader.readAsDataURL(file);
  }

  function addTask() {
    const text = document.getElementById("task-input").value.trim();
    const date = document.getElementById("task-date").value;
    const priority = document.getElementById("task-priority").value;
    if (!text || !date || !priority) return alert("Please fill all fields.");

    const user = getUserData();
    user.tasks.push({ text, date, priority, done: false });
    saveUserData(user);
    document.getElementById("task-input").value = "";
    renderTasks();
    renderProgress();
  }

  function renderTasks() {
    const user = getUserData();
    const taskList = document.getElementById("task-list");
    const completedList = document.getElementById("completed-list");
    taskList.innerHTML = "";
    completedList.innerHTML = "";

    user.tasks.forEach((task, index) => {
      const li = document.createElement("li");
      li.className = task.priority.toLowerCase();
      li.innerHTML = `
        <div>
          <strong>${task.text}</strong><br>
          <small>${task.date} • ${task.priority}</small>
        </div>`;

      if (!task.done) {
        const btn = document.createElement("button");
        btn.innerText = "✓";
        btn.onclick = () => {
          task.done = true;
          saveUserData(user);
          renderTasks();
          renderProgress();
        };
        li.appendChild(btn);
        taskList.appendChild(li);
      } else {
        completedList.appendChild(li);
      }
    });
  }

  function renderProgress() {
    const user = getUserData();
    const total = user.tasks.length;
    const completed = user.tasks.filter(t => t.done).length;
    const percent = total === 0 ? 0 : Math.round((completed / total) * 100);

    const ring = document.getElementById("progress-ring");
    const label = document.getElementById("progress-percent");

    if (ring && label) {
      const radius = ring.r.baseVal.value;
      const circumference = 2 * Math.PI * radius;
      ring.style.strokeDasharray = `${circumference}`;
      ring.style.strokeDashoffset = `${circumference - (percent / 100 * circumference)}`;
      label.innerText = `${percent}%`;
    }
  }

  function logout() {
    localStorage.removeItem("currentUser");
    window.location.href = "login.html";
  }

  function showSection(section) {
    ["tasks", "completed", "settings"].forEach(id => {
      document.getElementById(id + "-section").classList.add("hidden");
    });
    document.getElementById(section + "-section").classList.remove("hidden");
  }

  function toggleTheme() {
    document.body.classList.toggle("dark-mode");
  }

  function exportTasks() {
    const dataStr = JSON.stringify(getUserData().tasks);
    const blob = new Blob([dataStr], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "smartplanner_tasks.json";
    a.click();
  }

  const importInput = document.createElement("input");
  importInput.type = "file";
  importInput.accept = ".json";
  importInput.style.display = "none";
  importInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function (e) {
      try {
        const tasks = JSON.parse(e.target.result);
        const user = getUserData();
        user.tasks = tasks;
        saveUserData(user);
        renderTasks();
        renderProgress();
      } catch {
        alert("Invalid JSON file");
      }
    };
    reader.readAsText(file);
  });
  document.body.appendChild(importInput);

  // Expose to global scope
  window.addTask = addTask;
  window.logout = logout;
  window.showSection = showSection;
  window.toggleTheme = toggleTheme;
  window.exportTasks = exportTasks;
  window.showImport = () => importInput.click();

  // Initial rendering
  renderTasks();
  renderProgress();
  showSection("tasks");
});
