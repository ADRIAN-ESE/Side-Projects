// script.js

// --- Global State Variables ---
let inventory = [];
let purchaseHistory = [];
let selectedCarIndex = null;
const INVENTORY_KEY = 'carInventory';
const PURCHASE_KEY = 'purchaseHistory';
const AUTH_KEY = 'isManagerAuthenticated';
const MANAGER_PASSWORD = 'password';

// --- UI Element References ---
const messageModal = document.getElementById('message-modal');
const modalTitle = document.getElementById('modal-title');
const modalMessage = document.getElementById('modal-message');

const customerInventoryList = document.getElementById('customer-inventory-list');
const managerInventoryList = document.getElementById('inventory-list');
const purchaseCarSection = document.getElementById('purchase-car-section');
const availableCarsSection = document.getElementById('available-cars-section');
const carPurchaseDetails = document.getElementById('car-purchase-details');
const purchaseHistoryList = document.getElementById('purchase-history-list');
const totalRevenueDisplay = document.getElementById('total-revenue');
const colorOptionsDiv = document.getElementById('color-options');

// --- JSON Data Embedded Directly ---
const initialInventoryData = [
  {
    "make": "Lamborghini",
    "model": "Aventador SVJ",
    "year": 2023,
    "price": 550000.0,
    "color": "Red"
  },
  {
    "make": "Ferrari",
    "model": "SF90 Stradale",
    "year": 2024,
    "price": 625000.0,
    "color": "Black"
  },
  {
    "make": "BMW",
    "model": "M5 Competition",
    "year": 2023,
    "price": 115000.0,
    "color": "White"
  },
  {
    "make": "Tesla",
    "model": "Model S Plaid",
    "year": 2024,
    "price": 130000.0,
    "color": "Silver"
  },
  {
    "make": "McLaren",
    "model": "765LT",
    "year": 2022,
    "price": 400000.0,
    "color": "Blue"
  },
  {
    "make": "Rolls-Royce",
    "model": "Phantom",
    "year": 2023,
    "price": 450000.0,
    "color": "Black"
  },
  {
    "make": "Aston Martin",
    "model": "DBS Superleggera",
    "year": 2023,
    "price": 330000.0,
    "color": "White"
  },
  {
    "make": "Nissan",
    "model": "GT-R Nismo",
    "year": 2023,
    "price": 220000.0,
    "color": "Red"
  },
  {
    "make": "Toyota",
    "model": "Camry",
    "year": 2022,
    "price": 25000.0,
    "color": "Silver"
  },
  {
    "make": "Chevrolet",
    "model": "Malibu",
    "year": 2020,
    "price": 22000.0,
    "color": "White"
  },
  {
    "make": "Lamborghini",
    "model": "Aventador SVJ",
    "year": 2023,
    "price": 600000.0,
    "color": "Black"
  },
  {
    "make": "McLaren",
    "model": "765LT",
    "year": 2022,
    "price": 400000.0,
    "color": "White"
  }
];

// --- Core Functionality ---

/**
 * Loads the car inventory and purchase history from local storage or the hardcoded data.
 */
function loadData() {
    const storedInventory = localStorage.getItem(INVENTORY_KEY);
    const storedPurchases = localStorage.getItem(PURCHASE_KEY);

    if (storedInventory) {
        inventory = JSON.parse(storedInventory);
    } else {
        // Use the hardcoded data if local storage is empty
        inventory = initialInventoryData;
        saveData(); 
    }
    
    if (storedPurchases) {
        purchaseHistory = JSON.parse(storedPurchases);
    }
}

/**
 * Saves the current car inventory and purchase history to local storage.
 */
function saveData() {
    try {
        localStorage.setItem(INVENTORY_KEY, JSON.stringify(inventory));
        localStorage.setItem(PURCHASE_KEY, JSON.stringify(purchaseHistory));
    } catch (e) {
        console.error("Failed to save data to local storage:", e);
    }
}

// --- UI Functions ---

/**
 * Displays a modal message to the user.
 * @param {string} title The title of the modal.
 * @param {string} message The message to display.
 */
function showModal(title, message) {
    if (modalTitle && modalMessage && messageModal) {
        modalTitle.innerText = title;
        modalMessage.innerText = message;
        messageModal.classList.remove('hidden');
    }
}

/**
 * Hides the modal message.
 */
function closeModal() {
    if (messageModal) {
        messageModal.classList.add('hidden');
    }
}

// --- Authentication Functions ---

/**
 * Handles the manager login process.
 */
function managerLogin() {
    const passwordInput = document.getElementById('password');
    if (passwordInput && passwordInput.value === MANAGER_PASSWORD) {
        localStorage.setItem(AUTH_KEY, 'true');
        window.location.href = 'manager.html';
    } else {
        showModal("Login Failed", "Incorrect password. Please try again.");
    }
}

/**
 * Logs the manager out and redirects to the home page.
 */
function logout() {
    localStorage.removeItem(AUTH_KEY);
    window.location.href = 'index.html';
}

/**
 * Checks if the manager is authenticated and redirects if not.
 */
function checkLogin() {
    const isAuthenticated = localStorage.getItem(AUTH_KEY) === 'true';
    if (!isAuthenticated) {
        window.location.href = 'login.html';
    }
}

// --- Manager Portal Functions ---

/**
 * Renders the current inventory to the DOM for the manager view.
 */
function renderManagerInventory() {
    if (!managerInventoryList) return;
    checkLogin(); // Ensure the user is logged in
    managerInventoryList.innerHTML = '';
    if (inventory.length === 0) {
        managerInventoryList.innerHTML = '<p class="text-gray-500">There are no cars in the inventory.</p>';
        return;
    }

    inventory.forEach((car, index) => {
        const carItem = document.createElement('div');
        carItem.className = 'car-card flex justify-between items-center';
        carItem.innerHTML = `
            <div class="flex-grow">
                <h3 class="text-lg font-medium">${car.year} ${car.make} ${car.model}</h3>
                <p class="text-gray-600">Price: $${car.price.toLocaleString()}</p>
                <p class="text-sm text-gray-400">Color: ${car.color || 'Not Specified'}</p>
                <div class="mt-2 flex items-center">
                    <label for="price-input-${index}" class="input-label mb-0 mr-2">New Price:</label>
                    <input type="number" id="price-input-${index}" class="w-24 p-1 text-sm rounded border border-gray-300" placeholder="e.g., 30000">
                    <button onclick="updatePrice(${index})" class="btn-primary btn-sm ml-2">Update</button>
                </div>
            </div>
            <button onclick="removeCar(${index})" class="btn-remove">
                Remove
            </button>
        `;
        managerInventoryList.appendChild(carItem);
    });

    renderPurchaseHistory();
}

/**
 * Adds a new car to the inventory from the input fields.
 */
function addCar() {
    const make = document.getElementById('car-make').value;
    const model = document.getElementById('car-model').value;
    const year = parseInt(document.getElementById('car-year').value);
    const price = parseFloat(document.getElementById('car-price').value);

    if (!make || !model || isNaN(year) || isNaN(price)) {
        showModal("Error", "Please fill in all fields with valid data.");
        return;
    }

    // Default color for new cars
    const newCar = { make, model, year, price, color: 'Not Specified' };
    inventory.push(newCar);
    
    document.getElementById('car-make').value = '';
    document.getElementById('car-model').value = '';
    document.getElementById('car-year').value = '';
    document.getElementById('car-price').value = '';

    saveData();
    renderManagerInventory();
    showModal("Car Added", `Successfully added a ${year} ${make} ${model}.`);
}

/**
 * Removes a car from the inventory by its index.
 * @param {number} index The index of the car to remove.
 */
function removeCar(index) {
    if (index >= 0 && index < inventory.length) {
        const removedCar = inventory.splice(index, 1)[0];
        saveData();
        renderManagerInventory();
        showModal("Car Removed", `Successfully removed the ${removedCar.year} ${removedCar.make} ${removedCar.model}.`);
    }
}

/**
 * Updates the price of a car.
 * @param {number} index The index of the car to update.
 */
function updatePrice(index) {
    const newPriceInput = document.getElementById(`price-input-${index}`);
    const newPrice = parseFloat(newPriceInput.value);

    if (isNaN(newPrice) || newPrice <= 0) {
        showModal("Error", "Please enter a valid price.");
        return;
    }

    if (index >= 0 && index < inventory.length) {
        inventory[index].price = newPrice;
        saveData();
        renderManagerInventory();
        showModal("Price Updated", `Price for the ${inventory[index].year} ${inventory[index].make} ${inventory[index].model} has been updated to $${newPrice.toLocaleString()}.`);
    }
}

/**
 * Handles importing a JSON file from the user's local machine.
 */
function importInventory() {
    const fileInput = document.getElementById('json-file-input');
    const file = fileInput.files[0];

    if (!file) {
        showModal("Error", "Please select a JSON file to import.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const newInventory = JSON.parse(e.target.result);
            if (Array.isArray(newInventory)) {
                inventory = newInventory;
                saveData();
                renderManagerInventory();
                showModal("Import Successful", `Successfully imported ${newInventory.length} cars from the JSON file.`);
            } else {
                showModal("Import Error", "The imported file is not a valid JSON array.");
            }
        } catch (error) {
            console.error(error);
            showModal("Import Error", "Failed to parse the JSON file. Please ensure the file is correctly formatted.");
        }
    };
    reader.readAsText(file);
}


/**
 * Renders the purchase history and calculates total revenue.
 */
function renderPurchaseHistory() {
    if (!purchaseHistoryList || !totalRevenueDisplay) return;

    purchaseHistoryList.innerHTML = '';
    let totalRevenue = 0;

    if (purchaseHistory.length === 0) {
        purchaseHistoryList.innerHTML = '<p class="text-gray-500">No cars have been purchased yet.</p>';
    } else {
        const table = document.createElement('table');
        table.className = 'w-full table-auto text-left whitespace-no-wrap purchase-table';
        table.innerHTML = `
            <thead>
                <tr class="text-gray-600 bg-gray-100">
                    <th class="px-4 py-3">Customer</th>
                    <th class="px-4 py-3">Car</th>
                    <th class="px-4 py-3">Price</th>
                    <th class="px-4 py-3">Color</th>
                    <th class="px-4 py-3">Payment</th>
                    <th class="px-4 py-3">Date</th>
                </tr>
            </thead>
            <tbody id="purchase-history-body"></tbody>
        `;
        purchaseHistoryList.appendChild(table);
        const tableBody = document.getElementById('purchase-history-body');

        purchaseHistory.forEach(purchase => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-200 hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-4 py-3">${purchase.customer.name}</td>
                <td class="px-4 py-3">${purchase.car.year} ${purchase.car.make} ${purchase.car.model}</td>
                <td class="px-4 py-3">$${purchase.car.price.toLocaleString()}</td>
                <td class="px-4 py-3">${purchase.car.color}</td>
                <td class="px-4 py-3">${purchase.paymentMethod}</td>
                <td class="px-4 py-3">${new Date(purchase.purchaseDate).toLocaleDateString()}</td>
            `;
            tableBody.appendChild(row);
            totalRevenue += purchase.car.price;
        });
    }

    totalRevenueDisplay.innerText = `$${totalRevenue.toLocaleString()}`;
}

// --- Customer Portal Functions ---

const availableColors = ["Red", "Blue", "Black", "White", "Silver"];

/**
 * Renders the current inventory to the DOM for the customer view.
 */
function renderCustomerInventory() {
    if (!customerInventoryList) return;
    customerInventoryList.innerHTML = '';
    if (inventory.length === 0) {
        customerInventoryList.innerHTML = '<p class="text-gray-500">Sorry, there are no cars available for purchase at this time.</p>';
        return;
    }

    inventory.forEach((car, index) => {
        const carItem = document.createElement('div');
        carItem.className = 'car-card flex justify-between items-center';
        carItem.innerHTML = `
            <div class="flex-grow">
                <h3 class="text-lg font-medium">${car.year} ${car.make} ${car.model}</h3>
                <p class="text-gray-600">Price: $${car.price.toLocaleString()}</p>
            </div>
            <button onclick="preparePurchase(${index})" class="btn-primary">
                Purchase
            </button>
        `;
        customerInventoryList.appendChild(carItem);
    });
}

/**
 * Prepares the purchase form for a selected car.
 * @param {number} index The index of the car to purchase.
 */
function preparePurchase(index) {
    if (!purchaseCarSection || !availableCarsSection || !carPurchaseDetails || !colorOptionsDiv) return;
    selectedCarIndex = index;
    const car = inventory[index];
    carPurchaseDetails.innerText = `You are about to purchase the ${car.year} ${car.make} ${car.model} for $${car.price.toLocaleString()}. Please enter your details below.`;

    // Render color options
    colorOptionsDiv.innerHTML = availableColors.map(color => `
        <div class="color-option" onclick="selectColor(this, '${color}')" data-color="${color}" style="background-color: ${color.toLowerCase()};"></div>
    `).join('');

    availableCarsSection.classList.add('hidden');
    purchaseCarSection.classList.remove('hidden');
}

/**
 * Handles color selection
 */
function selectColor(element, color) {
    const allOptions = document.querySelectorAll('.color-option');
    allOptions.forEach(option => option.classList.remove('selected'));
    element.classList.add('selected');
}

/**
 * Confirms the purchase and updates the inventory.
 */
function confirmPurchase() {
    const customerName = document.getElementById('customer-name').value;
    const customerAddress = document.getElementById('customer-address').value;
    const customerPhone = document.getElementById('customer-phone').value;
    const paymentMethod = document.getElementById('payment-method').value;
    const selectedColorElement = document.querySelector('.color-option.selected');
    const selectedColor = selectedColorElement ? selectedColorElement.dataset.color : 'Not Specified';

    if (!customerName || !customerAddress || !customerPhone) {
        showModal("Error", "Please fill in all customer details.");
        return;
    }
    
    if (selectedCarIndex === null) {
        showModal("Error", "Please select a car to purchase.");
        return;
    }

    const purchasedCar = inventory[selectedCarIndex];
    
    // Remove the car from the inventory
    inventory.splice(selectedCarIndex, 1);
    
    const newPurchase = {
        customer: {
            name: customerName,
            address: customerAddress,
            phone: customerPhone
        },
        car: {...purchasedCar, color: selectedColor},
        paymentMethod: paymentMethod,
        purchaseDate: new Date().toISOString()
    };
    purchaseHistory.push(newPurchase);

    saveData();
    
    // Clear form and reset view
    document.getElementById('customer-name').value = '';
    document.getElementById('customer-address').value = '';
    document.getElementById('customer-phone').value = '';
    cancelPurchase();

    renderCustomerInventory();

    showModal("Purchase Confirmed!", `Thank you, ${customerName}! You have successfully purchased the ${purchasedCar.year} ${purchasedCar.make} ${purchasedCar.model} in ${selectedColor}.`);
}

/**
 * Cancels the purchase and returns to the car list view.
 */
function cancelPurchase() {
    if (!purchaseCarSection || !availableCarsSection) return;
    selectedCarIndex = null;
    purchaseCarSection.classList.add('hidden');
    availableCarsSection.classList.remove('hidden');
}

// --- Initialization ---

window.onload = () => {
    // This is a crucial line, it ensures data is loaded before anything else
    loadData();
    
    const path = window.location.pathname;
    if (path.includes('manager.html')) {
        checkLogin();
        renderManagerInventory();
    } else if (path.includes('customer.html')) {
        renderCustomerInventory();
    }
};