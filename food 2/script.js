// 🌐 Orion Kitchen Web App Logic — Final Optimized Version

const MENU_KEY = "orion_menu";
const PASSWORD_KEY = "orion_password";
const SALES_KEY = "orion_sales";
const PREF_KEY = "orion_prefs";
const DEFAULT_PASSWORD = "admin123";

// ---------- Utility Functions ----------
function getData(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}
function setData(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}
function formatCurrency(num) {
  return "$" + parseFloat(num || 0).toFixed(2);
}
function randomID() {
  return Math.random().toString(36).substring(2, 9);
}

// ---------- Initialize Defaults ----------
function ensureDefaults() {
  if (!localStorage.getItem(MENU_KEY)) {
    fetch("menu.json")
      .then(r => r.json())
      .then(d => setData(MENU_KEY, d))
      .catch(() => setData(MENU_KEY, {}));
  }
  if (!localStorage.getItem(PASSWORD_KEY)) {
    setData(PASSWORD_KEY, DEFAULT_PASSWORD);
    alert(`🔑 Default Manager Password: ${DEFAULT_PASSWORD}`);
  }
}
ensureDefaults();

// ---------- Page Router ----------
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  if (path.includes("manager.html")) initManager();
  else if (path.includes("customer.html")) initCustomer();
});

// =========================================================
// ================ MANAGER DASHBOARD LOGIC =================
// =========================================================
function initManager() {
  const loginSection = document.getElementById("loginSection");
  const dashboard = document.getElementById("dashboardSection");
  const pwInput = document.getElementById("managerPassword");
  const loginBtn = document.getElementById("loginBtn");
  const loginError = document.getElementById("loginError");
  const toggleModeBtn = document.getElementById("toggleMode");
  const changePwBtn = document.getElementById("changePwBtn");

  const prefs = getData(PREF_KEY, { darkMode: false });
  document.body.classList.toggle("dark", prefs.darkMode);

  function updateModeLabel() {
    const label = document.getElementById("modeLabel");
    if (label)
      label.textContent = document.body.classList.contains("dark")
        ? "Dark"
        : "Light";
  }
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
      refreshStats();
    } else {
      loginError.textContent = "Incorrect password!";
    }
  });

  changePwBtn.addEventListener("click", () => {
    const newPw = prompt("Enter new password (min 6 chars):");
    if (newPw && newPw.length >= 6) {
      setData(PASSWORD_KEY, newPw);
      alert("✅ Password changed successfully!");
    } else if (newPw) {
      alert("❌ Password too short (min 6 chars).");
    }
  });

  // ---------- Inventory Table ----------
  function loadInventory() {
    const tableBody = document.querySelector("#inventoryTable tbody");
    const menu = getData(MENU_KEY, {});
    tableBody.innerHTML = "";

    Object.entries(menu).forEach(([name, info]) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${name}</td>
        <td>${info.quantity}</td>
        <td>${formatCurrency(info.price)}</td>
        <td>${info.description || ""}</td>
        <td>${info.category || "Uncategorized"}</td>
        <td>
          <button class="btn small success" data-edit="${name}">Edit</button>
          <button class="btn small danger" data-del="${name}">Del</button>
        </td>`;
      tableBody.appendChild(tr);
    });

    tableBody.querySelectorAll("[data-edit]").forEach(btn =>
      btn.addEventListener("click", () => openModal(btn.dataset.edit))
    );
    tableBody.querySelectorAll("[data-del]").forEach(btn =>
      btn.addEventListener("click", () => {
        const menu = getData(MENU_KEY, {});
        delete menu[btn.dataset.del];
        setData(MENU_KEY, menu);
        loadInventory();
        refreshStats();
      })
    );
    refreshStats();
  }

  // ---------- Add/Edit Modal ----------
  const modal = document.getElementById("itemModal");
  const saveBtn = document.getElementById("saveItemBtn");
  const cancelBtn = document.getElementById("cancelItemBtn");
  document.getElementById("addItemBtn").addEventListener("click", () => openModal());
  cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));

  function openModal(itemName = "") {
    modal.classList.remove("hidden");
    const menu = getData(MENU_KEY, {});
    const editing = !!itemName;
    const item = menu[itemName] || {};

    document.getElementById("modalTitle").textContent = editing
      ? "Edit Item"
      : "Add New Item";
    document.getElementById("itemName").value = itemName || "";
    document.getElementById("itemQty").value = item.quantity || 0;
    document.getElementById("itemPrice").value = item.price || 0;
    document.getElementById("itemCategory").value = item.category || "";
    document.getElementById("itemDesc").value = item.description || "";

    saveBtn.onclick = () => {
      const name = document.getElementById("itemName").value.trim().toLowerCase();
      if (!name) return alert("Enter a valid item name!");
      const qty = parseInt(document.getElementById("itemQty").value) || 0;
      const price = parseFloat(document.getElementById("itemPrice").value) || 0;
      const cat = document.getElementById("itemCategory").value.trim();
      const desc = document.getElementById("itemDesc").value.trim();

      menu[name] = { quantity: qty, price, category: cat, description: desc };
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

  // ---------- Sales Report Modal ----------
  const salesModal = document.getElementById("salesModal");
  const salesList = document.getElementById("salesList");
  const closeSalesBtn = document.getElementById("closeSalesBtn");
  const viewSalesBtn = document.getElementById("viewSalesBtn");
  const filterBtn = document.getElementById("filterSalesBtn");
  const totalSalesSum = document.getElementById("totalSalesSum");
  const downloadPdfBtn = document.getElementById("downloadPdfBtn");

  viewSalesBtn.addEventListener("click", () => {
    loadSalesReport();
    salesModal.classList.remove("hidden");
  });
  closeSalesBtn.addEventListener("click", () =>
    salesModal.classList.add("hidden")
  );

  function loadSalesReport(start = "", end = "") {
    const sales = getData(SALES_KEY, []);
    const menu = getData(MENU_KEY, {});
    const filtered = sales.filter(s => {
      const d = new Date(s.date);
      if (start && d < new Date(start)) return false;
      if (end && d > new Date(end)) return false;
      return true;
    });

    let total = 0;
    salesList.innerHTML = filtered.length
      ? filtered
          .map(s => {
            const date = new Date(s.date).toLocaleString();
            let itemsHTML = "";
            let saleTotal = 0;
            Object.entries(s.cart).forEach(([n, q]) => {
              const price = menu[n]?.price || 0;
              saleTotal += price * q;
              itemsHTML += `${q} × ${n}<br>`;
            });
            total += saleTotal;
            return `
              <div class="sale-card">
                <div class="sale-meta"><strong>${date}</strong><br>Payment: ${s.payment}</div>
                <div class="sale-cart">${itemsHTML}</div>
                <div class="sale-total">Total: <b>${formatCurrency(saleTotal)}</b></div>
              </div>`;
          })
          .join("")
      : `<p class="muted">No sales in this range.</p>`;

    totalSalesSum.textContent = `Total Earnings in Range: ${formatCurrency(total)}`;
    document.getElementById("totalEarnings").textContent = formatCurrency(
      getAllEarnings()
    );
  }

  filterBtn.addEventListener("click", () => {
    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;
    loadSalesReport(start, end);
  });

  downloadPdfBtn.addEventListener("click", () => {
    window.print(); // quick PDF via browser's print-to-pdf
  });

  // ---------- Stats Updater ----------
  function refreshStats() {
    const menu = getData(MENU_KEY, {});
    const totalItems = Object.keys(menu).length;
    const lowStock = Object.values(menu).filter(i => i.quantity <= 5).length;
    document.getElementById("totalItems").textContent = totalItems;
    document.getElementById("lowStock").textContent = lowStock;
    document.getElementById("totalEarnings").textContent = formatCurrency(
      getAllEarnings()
    );
  }

  function getAllEarnings() {
    const sales = getData(SALES_KEY, []);
    const menu = getData(MENU_KEY, {});
    return sales.reduce((sum, s) => {
      let total = 0;
      Object.entries(s.cart).forEach(([n, q]) => {
        const price = menu[n]?.price || 0;
        total += price * q;
      });
      return sum + total;
    }, 0);
  }
}

// =========================================================
// ================== CUSTOMER INTERFACE ====================
// =========================================================
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
        <button class="btn success small" data-add="${name}">Add</button>`;
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
    Object.entries(cart).forEach(([n, q]) => {
      const price = menu[n].price * q;
      total += price;
      const div = document.createElement("div");
      div.className = "cart-item";
      div.innerHTML = `
        <span>${n} × ${q}</span>
        <span>${formatCurrency(price)}</span>
        <button class="btn small danger" data-remove="${n}">✕</button>`;
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

  searchBox.addEventListener("input", e => loadMenu(e.target.value));

  document.getElementById("checkoutBtn").addEventListener("click", () => {
    if (Object.keys(cart).length === 0) return alert("Cart is empty!");
    const menu = getData(MENU_KEY, {});
    let lines = "";
    let total = 0;
    Object.entries(cart).forEach(([n, q]) => {
      const price = menu[n].price * q;
      lines += `${q} × ${n} = ${formatCurrency(price)}\n`;
      total += price;
    });
    const receipt = `--- Orion Kitchen Receipt ---\n${lines}\nTotal: ${formatCurrency(total)}\n`;
    receiptPreview.textContent = receipt;
    checkoutModal.classList.remove("hidden");
  });

  document.getElementById("cancelCheckout").addEventListener("click", () => {
    checkoutModal.classList.add("hidden");
  });

  document.getElementById("confirmCheckout").addEventListener("click", () => {
    const method = document.getElementById("paymentMethod").value;
    const sales = getData(SALES_KEY, []);
    const menu = getData(MENU_KEY, {});
    Object.entries(cart).forEach(([n, q]) => {
      menu[n].quantity -= q;
      if (menu[n].quantity < 0) menu[n].quantity = 0;
    });
    sales.push({ id: randomID(), cart, payment: method, date: new Date().toISOString() });
    setData(SALES_KEY, sales);
    setData(MENU_KEY, menu);

    alert("✅ Payment complete! Print your receipt (Ctrl+P).");
    checkoutModal.classList.add("hidden");
    cart = {};
    refreshCart();
    loadMenu();
  });

  loadMenu();
}
