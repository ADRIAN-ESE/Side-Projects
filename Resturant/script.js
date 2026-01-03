// 🌐 Orion Kitchen Web App Logic (localStorage-only, improved version)

// ---------- GLOBALS ----------
const MENU_KEY = "orion_menu";
const PASSWORD_KEY = "orion_password";
const SALES_KEY = "orion_sales";
const PREF_KEY = "orion_prefs";

// Default password for first run
const DEFAULT_PASSWORD = "admin123";

// ---------- UTILS ----------
function getData(key, fallback) {
  const raw = localStorage.getItem(key);
  return raw ? JSON.parse(raw) : fallback;
}
function setData(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}
function formatCurrency(num) {
  return `$${parseFloat(num || 0).toFixed(2)}`;
}
function randomID() {
  return Math.random().toString(36).substring(2, 10);
}

// ---------- INIT ----------
function ensureDefaults() {
  if (!localStorage.getItem(MENU_KEY)) {
    fetch("menu.json")
      .then(r => r.json())
      .then(d => setData(MENU_KEY, d))
      .catch(() => setData(MENU_KEY, {}));
  }
  if (!localStorage.getItem(PASSWORD_KEY)) {
    setData(PASSWORD_KEY, DEFAULT_PASSWORD);
    alert(`🔑 First run password: ${DEFAULT_PASSWORD}`);
  }
}
ensureDefaults();

// ---------- PAGE ROUTING ----------
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  if (path.includes("manager.html")) initManager();
  else if (path.includes("customer.html")) initCustomer();
});

// ---------- MANAGER PAGE ----------
function initManager() {
  const loginSection = document.getElementById("loginSection");
  const dashboard = document.getElementById("dashboardSection");
  const loginBtn = document.getElementById("loginBtn");
  const pwInput = document.getElementById("managerPassword");
  const loginError = document.getElementById("loginError");
  const toggleModeBtn = document.getElementById("toggleMode");
  const changePwBtn = document.getElementById("changePwBtn");

  // Dark mode memory
  const prefs = getData(PREF_KEY, { darkMode: false });
  document.body.classList.toggle("dark", prefs.darkMode);
  updateModeLabel();

  toggleModeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    prefs.darkMode = document.body.classList.contains("dark");
    setData(PREF_KEY, prefs);
    updateModeLabel();
  });

  loginBtn.addEventListener("click", () => {
    const stored = getData(PASSWORD_KEY, DEFAULT_PASSWORD);
    if (pwInput.value === stored) {
      loginSection.classList.add("hidden");
      dashboard.classList.remove("hidden");
      loadInventory();
    } else {
      loginError.textContent = "Incorrect password.";
    }
  });

  // Password change handler
  changePwBtn.addEventListener("click", () => {
    const newPw = prompt("Enter new password (min 6 chars):");
    if (newPw && newPw.length >= 6) {
      setData(PASSWORD_KEY, newPw);
      alert("✅ Password changed successfully!");
    } else if (newPw) {
      alert("Password too short. Minimum 6 characters.");
    }
  });

  // Update mode label
  function updateModeLabel() {
    const modeLabel = document.getElementById("modeLabel");
    if (modeLabel) modeLabel.textContent = document.body.classList.contains("dark") ? "Dark" : "Light";
  }

  // ---------- Inventory Rendering ----------
  function loadInventory() {
    const tableBody = document.querySelector("#inventoryTable tbody");
    const menu = getData(MENU_KEY, {});
    tableBody.innerHTML = "";

    let lowCount = 0;
    let totalCount = 0;

    Object.entries(menu).forEach(([name, info]) => {
      totalCount++;
      if (info.quantity <= 5) lowCount++;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${name}</td>
        <td>${info.quantity}</td>
        <td>${info.price}</td>
        <td>${info.description || ""}</td>
        <td>${info.category || "Uncategorized"}</td>
        <td>
          <button class="btn small success" data-edit="${name}">Edit</button>
          <button class="btn small danger" data-delete="${name}">Del</button>
        </td>`;
      tableBody.appendChild(tr);
    });

    // Update stat counters
    document.getElementById("totalItems").textContent = totalCount;
    document.getElementById("lowStock").textContent = lowCount;

    // Edit/Delete actions
    tableBody.querySelectorAll("[data-edit]").forEach(btn => {
      btn.addEventListener("click", () => openModal(btn.dataset.edit));
    });
    tableBody.querySelectorAll("[data-delete]").forEach(btn => {
      btn.addEventListener("click", () => {
        const menu = getData(MENU_KEY, {});
        delete menu[btn.dataset.delete];
        setData(MENU_KEY, menu);
        loadInventory();
      });
    });
  }

  // ---------- Modal Handling ----------
  const modal = document.getElementById("itemModal");
  const saveBtn = document.getElementById("saveItemBtn");
  const cancelBtn = document.getElementById("cancelItemBtn");

  document.getElementById("addItemBtn").addEventListener("click", () => openModal());
  cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));

  function openModal(itemName = "") {
    modal.classList.remove("hidden");
    const menu = getData(MENU_KEY, {});
    const isEdit = !!itemName;
    document.getElementById("modalTitle").textContent = isEdit ? "Edit Item" : "Add New Item";

    const item = menu[itemName] || {};
    document.getElementById("itemName").value = itemName || "";
    document.getElementById("itemQty").value = item.quantity || 0;
    document.getElementById("itemPrice").value = item.price || 0;
    document.getElementById("itemCategory").value = item.category || "";
    document.getElementById("itemDesc").value = item.description || "";

    saveBtn.onclick = () => {
      const name = document.getElementById("itemName").value.trim().toLowerCase();
      const qty = parseInt(document.getElementById("itemQty").value) || 0;
      const price = parseFloat(document.getElementById("itemPrice").value) || 0;
      const category = document.getElementById("itemCategory").value.trim();
      const desc = document.getElementById("itemDesc").value.trim();
      if (!name) return alert("Item name required.");

      menu[name] = { quantity: qty, price, description: desc, category };
      setData(MENU_KEY, menu);
      modal.classList.add("hidden");
      loadInventory();
    };
  }

  // ---------- Export CSV ----------
  document.getElementById("exportBtn").addEventListener("click", () => {
    const menu = getData(MENU_KEY, {});
    let csv = "Item,Quantity,Price,Description,Category\n";
    Object.entries(menu).forEach(([k, v]) => {
      csv += `"${k}",${v.quantity},${v.price},"${v.description || ""}","${v.category || ""}"\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "menu_export.csv";
    a.click();
  });
}

// ---------- CUSTOMER PAGE ----------
function initCustomer() {
  const menuList = document.getElementById("menuList");
  const cartDiv = document.getElementById("cartItems");
  const totalDisplay = document.getElementById("totalDisplay");
  const checkoutModal = document.getElementById("checkoutModal");
  const receiptPreview = document.getElementById("receiptPreview");
  const searchBox = document.getElementById("searchBox");

  let cart = {};

  function loadMenu(filter = "") {
    const menu = getData(MENU_KEY, {});
    menuList.innerHTML = "";
    Object.entries(menu).forEach(([name, info]) => {
      if (info.quantity <= 0) return;
      if (filter && !name.toLowerCase().includes(filter.toLowerCase())) return;
      const div = document.createElement("div");
      div.className = "menu-item";
      div.innerHTML = `
        <h4>${name}</h4>
        <p>${info.description || ""}</p>
        <p><strong>${formatCurrency(info.price)}</strong></p>
        <button class="btn success small" data-add="${name}">Add</button>
      `;
      menuList.appendChild(div);
    });

    menuList.querySelectorAll("[data-add]").forEach(btn => {
      btn.addEventListener("click", () => {
        const menu = getData(MENU_KEY, {});
        const item = menu[btn.dataset.add];
        const qty = parseInt(prompt(`How many ${btn.dataset.add}?`, "1")) || 0;
        if (qty <= 0) return;
        if (qty > item.quantity) return alert("Not enough stock!");
        cart[btn.dataset.add] = (cart[btn.dataset.add] || 0) + qty;
        refreshCart();
      });
    });
  }

  function refreshCart() {
    const menu = getData(MENU_KEY, {});
    cartDiv.innerHTML = "";
    let total = 0;
    Object.entries(cart).forEach(([name, qty]) => {
      const price = menu[name].price * qty;
      total += price;
      const div = document.createElement("div");
      div.className = "cart-item";
      div.innerHTML = `
        <span>${name} × ${qty}</span>
        <span>${formatCurrency(price)}</span>
        <button class="btn small danger" data-remove="${name}">✕</button>
      `;
      cartDiv.appendChild(div);
    });
    totalDisplay.textContent = `Total: ${formatCurrency(total)}`;

    cartDiv.querySelectorAll("[data-remove]").forEach(btn => {
      btn.addEventListener("click", () => {
        delete cart[btn.dataset.remove];
        refreshCart();
      });
    });
  }

  // Search filter
  searchBox.addEventListener("input", e => loadMenu(e.target.value));

  // Checkout logic
  document.getElementById("checkoutBtn").addEventListener("click", () => {
    if (Object.keys(cart).length === 0) return alert("Cart is empty!");
    const menu = getData(MENU_KEY, {});
    let total = 0;
    let lines = "";
    Object.entries(cart).forEach(([n, q]) => {
      const price = menu[n].price * q;
      lines += `${q} × ${n} = ${formatCurrency(price)}\n`;
      total += price;
      menu[n].quantity -= q;
    });
    const receipt = `--- Orion Kitchen Receipt ---\n${lines}Total: ${formatCurrency(total)}\n`;
    receiptPreview.textContent = receipt;
    checkoutModal.classList.remove("hidden");
  });

  document.getElementById("cancelCheckout").addEventListener("click", () => {
    checkoutModal.classList.add("hidden");
  });

  document.getElementById("confirmCheckout").addEventListener("click", () => {
    const method = document.getElementById("paymentMethod").value;
    const sales = getData(SALES_KEY, []);
    sales.push({
      id: randomID(),
      cart,
      payment: method,
      date: new Date().toISOString()
    });
    setData(SALES_KEY, sales);

    // Update menu quantities
    const menu = getData(MENU_KEY, {});
    Object.entries(cart).forEach(([n, q]) => {
      menu[n].quantity -= q;
      if (menu[n].quantity < 0) menu[n].quantity = 0;
    });
    setData(MENU_KEY, menu);

    alert("✅ Payment complete! You can print your receipt (Ctrl+P).");
    checkoutModal.classList.add("hidden");
    cart = {};
    refreshCart();
    loadMenu();
  });

  loadMenu();
}
