const LOW_STOCK = 5;
const app = document.getElementById("app");

/* ---------- STORAGE ---------- */

function load(key, fallback) {
    try {
        return JSON.parse(localStorage.getItem(key)) ?? fallback;
    } catch {
        return fallback;
    }
}

function save(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

/* ---------- INITIAL DATA ---------- */

let users = load("users", {
    manager: {
        password: hash("admin123"),
        role: "manager",
        business: "MAIN_BUSINESS"
    }
});

let inventory = load("inventory", {});
let currentUser = null;

save("users", users);

/* ---------- UTIL ---------- */

function hash(text) {
    return btoa(text);
}

function clear() {
    app.innerHTML = "";
}

/* ---------- LOGIN ---------- */

function showLogin() {
    clear();
    app.innerHTML = `
        <div class="container">
            <h2>Inventory Manager</h2>
            <input id="user" placeholder="Username">
            <input id="pass" type="password" placeholder="Password">
            <input id="biz" placeholder="Business (for registration)">
            <button onclick="login()">Login</button>
            <button onclick="register()">Register</button>
        </div>
    `;
}

function login() {
    const u = user.value.trim();
    const p = pass.value.trim();

    if (users[u] && users[u].password === hash(p)) {
        currentUser = users[u];
        showDashboard();
    } else {
        alert("Invalid credentials");
    }
}

function register() {
    const u = user.value.trim();
    const p = pass.value.trim();
    const b = biz.value.trim();

    if (!u || !p || !b) return alert("Fill all fields");
    if (users[u]) return alert("User exists");

    users[u] = { password: hash(p), role: "user", business: b };
    save("users", users);
    alert("Account created");
}

/* ---------- DASHBOARD ---------- */

function showDashboard() {
    clear();
    const biz = currentUser.business;
    inventory[biz] ??= {};
    save("inventory", inventory);

    app.innerHTML = `
        <div class="header">
            <strong>${biz} | ${currentUser.role.toUpperCase()}</strong>
            <button onclick="showLogin()">Logout</button>
        </div>

        <div class="main">
            <div class="sidebar">
                <button onclick="inventoryView()">Inventory</button>
                <button onclick="alert('Sales coming soon')">Sales</button>
                <button onclick="alert('Reports coming soon')">Reports</button>
                ${currentUser.role === "manager"
        ? `<button class="danger">User Management</button>`
        : ""}
            </div>
            <div class="content" id="content"></div>
        </div>
    `;

    inventoryView();
}

/* ---------- INVENTORY ---------- */

function inventoryView() {
    const biz = currentUser.business;
    const content = document.getElementById("content");

    content.innerHTML = `
        <h2>Inventory</h2>
        <input id="search" placeholder="Search">
        <div id="list"></div>
        <button onclick="addItem()">Add Item</button>
        <button onclick="sortBy('price')">Sort by Price</button>
        <button onclick="sortBy('qty')">Sort by Qty</button>
        <button onclick="sortBy('name')">Sort by Name</button>
    `;

    search.oninput = render;
    render();
}

function render() {
    const biz = currentUser.business;
    const list = document.getElementById("list");
    const filter = search.value.toLowerCase();

    list.innerHTML = "";

    Object.entries(inventory[biz]).forEach(([id, v]) => {
        if ((v.name + v.category).toLowerCase().includes(filter)) {
            const low = v.qty <= LOW_STOCK ? "low" : "";
            list.innerHTML += `
                <div class="item ${low}">
                    ${id} | ${v.name} | ${v.category} |
                    Qty: ${v.qty} | ₦${v.price}
                </div>
            `;
        }
    });
}

function addItem() {
    const id = prompt("Item ID");
    const name = prompt("Name");
    const cat = prompt("Category");
    const qty = Number(prompt("Quantity"));
    const price = Number(prompt("Price"));

    if (!id || !name || isNaN(qty) || isNaN(price)) return;

    inventory[currentUser.business][id] = { name, category: cat, qty, price };
    save("inventory", inventory);
    render();
}

function sortBy(key) {
    const biz = currentUser.business;
    inventory[biz] = Object.fromEntries(
        Object.entries(inventory[biz]).sort((a, b) =>
            a[1][key] > b[1][key] ? 1 : -1
        )
    );
    save("inventory", inventory);
    render();
}

/* ---------- START ---------- */

showLogin();
