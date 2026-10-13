const API = "";
let customizationOptions = [];
let simulatedTime = null;
let menuRequestId = 0;
const currencyFormatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function sliderTime(value) {
    const minutes = Number(value);
    return `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
}

function sizePriceHtml(info) {
    const price = `<span class="effective-price">$${info.price.toFixed(2)}</span>`;
    return info.discount_rate > 0
        ? `<del class="original-price">$${info.original_price.toFixed(2)}</del>${price}`
        : price;
}

async function loadCustomizations() {
    try {
        const res = await fetch(`${API}/api/customizations`);
        const data = await res.json();
        customizationOptions = data.customizations;
    } catch (err) {
        customizationOptions = [];
    }
}

function updatePrice(itemId) {
    const sizeRadio = document.querySelector(`input[name="size-${itemId}"]:checked`);
    if (!sizeRadio) return;
    let total = Math.round(parseFloat(sizeRadio.dataset.price) * 100);
    document.querySelectorAll(`input[name="custom-${itemId}"]:checked`).forEach((cb) => {
        total += Math.round(parseFloat(cb.dataset.price) * 100);
    });
    document.getElementById(`price-${itemId}`).textContent = (total / 100).toFixed(2);
}

async function loadMenu() {
    const container = document.getElementById("menu-list");
    const requestId = ++menuRequestId;
    const status = document.getElementById("pricing-status");
    status.textContent = "Updating prices...";
    container.querySelectorAll(".order-btn").forEach((button) => (button.disabled = true));
    try {
        const query = simulatedTime === null ? "" : `?time=${encodeURIComponent(simulatedTime)}`;
        const res = await fetch(`${API}/api/menu${query}`);
        if (!res.ok) throw new Error("Pricing request failed");
        const data = await res.json();
        if (requestId !== menuRequestId) return;
        const selections = new Map(data.items.map((item) => [item.id, {
            size: container.querySelector(`input[name="size-${item.id}"]:checked`)?.value || "medium",
            customizations: Array.from(container.querySelectorAll(`input[name="custom-${item.id}"]:checked`), (input) => input.value),
        }]));
        container.innerHTML = "";

        data.items.forEach((item) => {
            const card = document.createElement("div");
            card.className = "menu-card";
            const selection = selections.get(item.id);

            const sizesHtml = Object.entries(item.sizes)
                .map(
                    ([size, info]) =>
                        `<label class="size-option">
                            <input type="radio" name="size-${item.id}" value="${size}"
                                data-price="${info.price}"
                                data-original-price="${info.original_price}"
                                data-pricing-tier="${info.pricing_tier}"
                                data-effective-time="${info.effective_time}"
                                ${size === selection.size ? "checked" : ""}>
                            <span class="size-label">${size.charAt(0).toUpperCase() + size.slice(1)}</span>
                            <span class="size-price">${sizePriceHtml(info)}</span>
                        </label>`
                )
                .join("");

            const customizationsHtml = customizationOptions
                .map(
                    (opt) =>
                        `<label class="customization-option">
                            <input type="checkbox" name="custom-${item.id}" value="${opt.id}"
                                data-price="${opt.price}" ${selection.customizations.includes(opt.id) ? "checked" : ""}>
                            <span class="custom-label">${opt.name}</span>
                            <span class="custom-price">+$${opt.price.toFixed(2)}</span>
                        </label>`
                )
                .join("");

            const defaultPrice = item.sizes.medium
                ? item.sizes.medium.price.toFixed(2)
                : Object.values(item.sizes)[0].price.toFixed(2);

            card.innerHTML = `
                <h3>${item.name}</h3>
                <p class="description">${item.description}</p>
                <div class="size-selector">
                    ${sizesHtml}
                </div>
                ${customizationsHtml ? `<div class="customization-group">${customizationsHtml}</div>` : ""}
                <button class="order-btn" onclick="placeOrder('${item.id}')">
                    Order - $<span id="price-${item.id}">${defaultPrice}</span>
                </button>
            `;
            container.appendChild(card);
            updatePrice(item.id);

            // Update displayed price when size or customization selection changes
            card.querySelectorAll(`input[name="size-${item.id}"]`).forEach(
                (radio) => {
                    radio.addEventListener("change", () => updatePrice(item.id));
                }
            );
            card.querySelectorAll(`input[name="custom-${item.id}"]`).forEach(
                (cb) => {
                    cb.addEventListener("change", () => updatePrice(item.id));
                }
            );
        });
        const info = Object.values(data.items[0].sizes)[0];
        const [hours, minutes] = info.effective_time.split(":").map(Number);
        const slider = document.getElementById("pricing-slider");
        slider.value = hours * 60 + minutes;
        slider.disabled = false;
        document.getElementById("pricing-time").textContent = info.effective_time;
        document.getElementById("pricing-timezone").textContent = info.pricing_timezone;
        document.getElementById("pricing-mode").textContent = simulatedTime === null ? "Server time" : "Simulated time";
        document.getElementById("pricing-reset").disabled = simulatedTime === null;
        const tier = document.getElementById("pricing-tier");
        tier.textContent = info.pricing_tier === "Peak" ? "Peak Pricing" : "Off-Peak Pricing - 20% Off";
        tier.classList.toggle("off-peak", info.pricing_tier === "Off-Peak");
        status.textContent = "";
    } catch (err) {
        if (requestId !== menuRequestId) return;
        status.textContent = "Prices unavailable. Retry with the time controls.";
        if (!container.querySelector(".menu-card")) {
            container.innerHTML = `<p class="empty-state">Failed to load menu.</p>`;
        }
        document.getElementById("pricing-reset").disabled = false;
    }
}

let pendingOrder = null;

function placeOrder(itemId) {
    const selectedRadio = document.querySelector(
        `input[name="size-${itemId}"]:checked`
    );
    if (!selectedRadio || document.getElementById("pricing-status").textContent) return;
    const size = selectedRadio.value;
    const sizePrice = parseFloat(selectedRadio.dataset.price);
    const originalPrice = parseFloat(selectedRadio.dataset.originalPrice);
    const tier = selectedRadio.dataset.pricingTier;

    const customizations = [];
    const customizationDetails = [];
    document.querySelectorAll(`input[name="custom-${itemId}"]:checked`).forEach((cb) => {
        customizations.push(cb.value);
        const opt = customizationOptions.find((o) => o.id === cb.value);
        if (opt) customizationDetails.push({ name: opt.name, price: opt.price });
    });

    const card = selectedRadio.closest(".menu-card");
    const drinkName = card.querySelector("h3").textContent;
    const total = (Math.round(sizePrice * 100) + customizationDetails.reduce((sum, custom) => sum + Math.round(custom.price * 100), 0)) / 100;

    pendingOrder = { itemId, size, customizations, time: selectedRadio.dataset.effectiveTime };
    showConfirmation(drinkName, size, originalPrice, customizationDetails, total, tier, originalPrice - sizePrice);
}

function showConfirmation(drinkName, size, basePrice, customizations, total, tier, discount) {
    const summary = document.getElementById("confirm-summary");
    let html = `<div class="confirm-drink-line">${drinkName} &mdash; ${size.charAt(0).toUpperCase() + size.slice(1)}</div>`;
    html += `<div class="quote-tier">${tier} Pricing</div>`;
    html += `<div class="confirm-custom-item"><span>Base Price</span><span>$${basePrice.toFixed(2)}</span></div>`;
    if (tier === "Off-Peak") {
        html += `<div class="confirm-custom-item discount-line"><span>Off-Peak Discount (20%)</span><span>-$${discount.toFixed(2)}</span></div>`;
    }

    if (customizations.length > 0) {
        html += `<div class="confirm-customizations">`;
        customizations.forEach((c) => {
            html += `<div class="confirm-custom-item"><span>${c.name}</span><span>$${c.price.toFixed(2)}</span></div>`;
        });
        html += `</div>`;
    }

    html += `<div class="confirm-total"><span>Subtotal</span><span>$${total.toFixed(2)}</span></div>`;
    summary.innerHTML = html;

    document.getElementById("confirm-overlay").classList.remove("hidden");
}

function closeConfirmation() {
    if (document.getElementById("confirm-order-btn").disabled) return;
    document.getElementById("confirm-overlay").classList.add("hidden");
    pendingOrder = null;
}

async function submitPendingOrder() {
    const confirmButton = document.getElementById("confirm-order-btn");
    if (!pendingOrder || confirmButton.disabled) return;
    const { itemId, size, customizations, time } = pendingOrder;
    confirmButton.disabled = true;
    document.getElementById("confirm-back-btn").disabled = true;

    try {
        const res = await fetch(`${API}/api/orders`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: itemId, size, customizations, time }),
        });
        if (!res.ok) throw new Error("Order failed");

        document.querySelectorAll(`input[name="custom-${itemId}"]`).forEach(
            (cb) => (cb.checked = false)
        );
        updatePrice(itemId);

        confirmButton.disabled = false;
        closeConfirmation();
        await loadOrders();
        await loadFinancials();
    } catch (err) {
        alert("Failed to place order: " + err.message);
    } finally {
        confirmButton.disabled = false;
        document.getElementById("confirm-back-btn").disabled = false;
    }
}

async function advanceOrder(orderId, nextStatus) {
    try {
        const res = await fetch(`${API}/api/orders/${orderId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: nextStatus }),
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Update failed");
        }
        await loadOrders();
        await loadFinancials();
    } catch (err) {
        alert("Failed to update order: " + err.message);
    }
}

async function cancelOrder(orderId) {
    try {
        const res = await fetch(`${API}/api/orders/${orderId}`, {
            method: "DELETE",
        });
        if (!res.ok) throw new Error("Cancel failed");
        await loadOrders();
        await loadFinancials();
    } catch (err) {
        alert("Failed to cancel order: " + err.message);
    }
}

function getAdvanceButton(order) {
    const nextMap = {
        pending: { status: "preparing", label: "Start Preparing" },
        preparing: { status: "ready", label: "Mark Ready" },
        ready: { status: "completed", label: "Complete" },
    };
    const next = nextMap[order.status];
    if (!next) return "";
    return `<button class="advance-btn" onclick="advanceOrder(${order.order_id}, '${next.status}')">${next.label}</button>`;
}

function renderReceipt(detail) {
    const sizeName = detail.size.charAt(0).toUpperCase() + detail.size.slice(1);
    let html = `<div class="receipt-tier">${detail.pricing_tier} Pricing</div>`;
    html += `<div class="receipt-line base-item"><span>${detail.item_name} (${sizeName})</span><span>$${detail.base_price.toFixed(2)}</span></div>`;
    if (detail.pricing_tier === "Off-Peak") {
        html += `<div class="receipt-line discount-line"><span>Off-Peak Discount (20%)</span><span>-$${detail.discount_amount.toFixed(2)}</span></div>`;
    }

    detail.customizations.forEach((c) => {
        html += `<div class="receipt-line customization"><span>${c.name}</span><span>$${c.price.toFixed(2)}</span></div>`;
    });

    html += `<div class="receipt-line subtotal"><span>Subtotal</span><span>$${detail.subtotal.toFixed(2)}</span></div>`;
    html += `<div class="receipt-line tax"><span>Tax (8.5%)</span><span>$${detail.tax.toFixed(2)}</span></div>`;
    html += `<div class="receipt-line total"><span>Total</span><span>$${detail.total.toFixed(2)}</span></div>`;

    return `<div class="receipt-panel">${html}</div>`;
}

function toggleReceipt(orderId) {
    const orderEl = document.getElementById(`order-${orderId}`);
    const wrapper = orderEl.querySelector(".receipt-wrapper");
    const btn = orderEl.querySelector(".receipt-btn");
    if (wrapper.style.display === "none") {
        wrapper.style.display = "";
        btn.textContent = "Hide Receipt";
    } else {
        wrapper.style.display = "none";
        btn.textContent = "View Receipt";
    }
}

function renderOrder(order) {
    const div = document.createElement("div");
    div.className = "order-item";
    div.id = `order-${order.order_id}`;
    const cancelBtn =
        order.status === "pending"
            ? `<button class="cancel-btn" onclick="cancelOrder(${order.order_id})">Cancel</button>`
            : "";
    const receiptBtn =
        order.status === "completed" && order.items_detail
            ? `<button class="receipt-btn" onclick="toggleReceipt(${order.order_id})">View Receipt</button>`
            : "";
    const receiptPanel =
        order.status === "completed" && order.items_detail
            ? `<div class="receipt-wrapper" style="display:none">${renderReceipt(order.items_detail)}</div>`
            : "";

    div.innerHTML = `
        <div class="order-row">
            <div class="order-info">
                <span class="order-id">#${order.order_id}</span>
                <span class="order-items">${order.items.join(", ")}</span>
                <span class="order-price">$${order.total_price.toFixed(2)}</span>
            </div>
            <span class="order-status status-${order.status}">${order.status}</span>
            ${getAdvanceButton(order)}
            ${cancelBtn}
            ${receiptBtn}
        </div>
        ${receiptPanel}
    `;
    return div;
}

async function loadOrders() {
    const container = document.getElementById("orders-list");
    try {
        const res = await fetch(`${API}/api/orders`);
        const data = await res.json();

        if (data.orders.length === 0) {
            container.innerHTML = `<p class="empty-state">No orders yet. Pick a drink from the menu!</p>`;
            return;
        }

        const active = data.orders.filter(
            (o) => o.status === "pending" || o.status === "preparing" || o.status === "ready"
        );
        const completed = data.orders.filter((o) => o.status === "completed");

        container.innerHTML = "";

        if (active.length > 0) {
            const heading = document.createElement("p");
            heading.className = "order-group-heading";
            heading.textContent = "Active Orders";
            container.appendChild(heading);
            active.forEach((order) => container.appendChild(renderOrder(order)));
        }

        if (completed.length > 0) {
            const heading = document.createElement("p");
            heading.className = "order-group-heading";
            heading.textContent = "Completed";
            container.appendChild(heading);
            completed.forEach((order) => container.appendChild(renderOrder(order)));
        }
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Failed to load orders.</p>`;
    }
}

async function loadFinancials() {
    try {
        const res = await fetch(`${API}/api/financials`);
        const data = await res.json();

        document.getElementById("metric-revenue").textContent = `$${data.total_revenue.toFixed(2)}`;
        document.getElementById("metric-cogs").textContent = `$${data.total_cogs.toFixed(2)}`;
        document.getElementById("metric-margin").textContent = currencyFormatter.format(data.margin);
        document.getElementById("metric-peak-revenue").textContent = `$${data.peak_revenue.toFixed(2)}`;
        document.getElementById("metric-off-peak-revenue").textContent = `$${data.off_peak_revenue.toFixed(2)}`;

        const container = document.getElementById("financials-table-container");
        if (data.orders.length === 0) {
            container.innerHTML = `<p class="empty-state">Place an order to see per-order financials.</p>`;
            return;
        }

        let html = `<table class="financials-table">
            <thead><tr>
                <th>Order</th><th>Drink</th><th>Tier</th><th>Revenue</th><th>COGS</th><th>Margin</th>
            </tr></thead><tbody>`;
        data.orders.forEach((o) => {
            html += `<tr>
                <td>#${o.order_id}</td>
                <td>${o.drink_name}</td>
                <td>${o.pricing_tier}</td>
                <td>$${o.revenue.toFixed(2)}</td>
                <td>$${o.cogs.toFixed(2)}</td>
                <td class="col-margin">${currencyFormatter.format(o.margin)}</td>
            </tr>`;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
    } catch (err) {
        // silently ignore — dashboard is supplementary
    }
}

// Load on page ready
document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("pricing-slider").addEventListener("input", (event) => {
        simulatedTime = sliderTime(event.target.value);
        document.getElementById("pricing-time").textContent = simulatedTime;
        loadMenu();
    });
    document.getElementById("pricing-reset").addEventListener("click", () => {
        simulatedTime = null;
        loadMenu();
    });
    setInterval(() => {
        if (simulatedTime === null) loadMenu();
    }, 60000);
    await loadCustomizations();
    loadMenu();
    loadOrders();
    loadFinancials();

    document.getElementById("confirm-order-btn").addEventListener("click", submitPendingOrder);
    document.getElementById("confirm-back-btn").addEventListener("click", closeConfirmation);
    document.getElementById("confirm-overlay").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeConfirmation();
    });
});
