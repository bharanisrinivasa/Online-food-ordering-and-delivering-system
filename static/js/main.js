document.addEventListener('DOMContentLoaded', () => {
    let globalFoods = {};
    let currentRestaurantId = null; 
    let cityLocation = null;
    let liveMap = null, liveMarker = null, routeLine = null;
    const cart = [];

    // Views
    const views = {
        'view-dashboard': document.getElementById('view-dashboard'),
        'view-foodorder': document.getElementById('view-foodorder'),
        'view-feedback': document.getElementById('view-feedback'),
        'view-history': document.getElementById('view-history')
    };

    // DOM Elements
    const foodGrid = document.getElementById('foodGrid');
    const invoiceList = document.getElementById('invoiceList');
    const searchInput = document.getElementById('locationSearchInput');
    const searchIcon = document.getElementById('searchIcon');

    // Modals
    const foodItemModal = document.getElementById('foodItemModal');
    const modalFoodImg = document.getElementById('modalFoodImg');
    const modalFoodName = document.getElementById('modalFoodName');
    const modalFoodDesc = document.getElementById('modalFoodDesc');
    const modalFoodPrice = document.getElementById('modalFoodPrice');
    const cancelFoodBtn = document.getElementById('cancelFoodBtn');
    const orderFoodBtn = document.getElementById('orderFoodBtn');

    const locationModal = document.getElementById('locationModal');
    const closeMapBtn = document.getElementById('closeMapBtn');
    const confirmOrderBtn = document.getElementById('confirmOrderBtn');

    let currentSelectedFood = null;

    // SPA Routing Sidebar
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('data-target');
            if (target === 'chatbotToggle') {
                const chatToggle = document.getElementById('chatbotToggle');
                if (chatToggle) chatToggle.click();
                return;
            }
            if (target === 'payment-success') {
                window.location.href = '/payment-success?sub=0&total=0';
                return;
            }
            if (target && views[target]) {
                // Remove active classes
                sidebarLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Hide all views, show targeted
                Object.values(views).forEach(v => { if (v) v.style.display = 'none'; });
                views[target].style.display = 'block';

                // Specific View Triggers
                if (target === 'view-history') loadHistory();
                if (target === 'view-foodorder') {
                    if (liveMap) setTimeout(() => liveMap.invalidateSize(), 300);
                }
            }
        });
    });

    // --- Search Logic ---
    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        foodGrid.innerHTML = '<p>Loading...</p>';
        try {
            const response = await fetch(`/api/search?location=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (!data.success) {
                foodGrid.innerHTML = `<h3>${data.message}</h3>`;
                cityLocation = null;
                return;
            }

            cityLocation = data.city_location; 
            renderRestaurants(data.restaurants);
        } catch (error) {
            console.error('Search error:', error);
            foodGrid.innerHTML = `<h3>Error contacting server.</h3>`;
        }
    }

    if (searchIcon) searchIcon.addEventListener('click', performSearch);
    if (searchInput) searchInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') performSearch(); });

    function renderRestaurants(restaurants) {
        if (!foodGrid) return;
        globalFoods = {}; 
        
        if (restaurants.length === 0) {
            foodGrid.innerHTML = `<h3>No restaurants found here.</h3>`;
            return;
        }

        let html = '';
        restaurants.forEach(rest => {
            currentRestaurantId = rest.id; 
            html += `<h3 style="width: 100%; margin: 20px 0 10px 0;">${rest.name}</h3>`;
            
            rest.menu.forEach(food => {
                const foodId = food.id;
                food.restaurant_id = rest.id;
                globalFoods[foodId] = food;

                html += `
                <div class="food-card" style="cursor: pointer;" onclick="openFoodModal('${foodId}')">
                    <img src="${food.image}" alt="${food.name}">
                    <h4>${food.name}</h4>
                    <div class="price-rating">
                        <span class="price">₹${food.price}</span>
                        <span class="rating">⭐ 4.5</span>
                    </div>
                </div>
                `;
            });
        });

        foodGrid.innerHTML = html;
    }

    // --- Food Modal Logic ---
    window.openFoodModal = function(foodId) {
        const food = globalFoods[foodId];
        if (!food) return;

        currentSelectedFood = food;
        modalFoodImg.src = food.image;
        modalFoodName.textContent = food.name;
        modalFoodDesc.textContent = food.description || 'Delicious meal';
        modalFoodPrice.textContent = `₹${food.price}`;
        foodItemModal.style.display = 'flex';
    };

    if (cancelFoodBtn) cancelFoodBtn.addEventListener('click', () => { foodItemModal.style.display = 'none'; });
    if (orderFoodBtn) orderFoodBtn.addEventListener('click', () => {
        if (currentSelectedFood) {
            addToCart(currentSelectedFood);
            foodItemModal.style.display = 'none';
        }
    });

    // --- Cart & Invoice Logic ---
    function addToCart(food) {
        cart.push(food);
        renderInvoice();
        updateSummary();
    }

    function renderInvoice() {
        if (!invoiceList) return;
        if (cart.length === 0) {
            invoiceList.innerHTML = '<p style="color: #a0aec0; text-align: center; margin-top: 20px;">Your cart is empty.</p>';
            return;
        }

        invoiceList.innerHTML = cart.map((item, index) => `
            <div class="invoice-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="invoice-info">
                    <h4>${item.name}</h4>
                    <div class="item-price">₹${item.price}</div>
                </div>
                <button style="margin-left:auto; background:none; border:none; color:#e74c3c; cursor:pointer;" onclick="removeFromCart(${index})">🗑️</button>
            </div>
        `).join('');
    }

    window.removeFromCart = function(index) {
        cart.splice(index, 1);
        renderInvoice();
        updateSummary();
    };

    function updateSummary() {
        const subTotalEl = document.getElementById('subTotal');
        const taxEl = document.getElementById('tax');
        const totalPaymentEl = document.getElementById('totalPayment');
        if (!subTotalEl || !taxEl || !totalPaymentEl) return;

        const subTotal = cart.reduce((sum, item) => sum + item.price, 0);
        const tax = subTotal > 0 ? 50 : 0;
        const total = subTotal + tax;

        subTotalEl.textContent = '₹' + subTotal;
        taxEl.textContent = '+₹' + tax;
        totalPaymentEl.textContent = '₹' + total;
    }

    // Payment method selection
    const methodBtns = document.querySelectorAll('.method-btn');
    methodBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            methodBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // --- Checkout / Map Logic ---
    const placeOrderBtn = document.getElementById('placeOrderBtn');
    let checkoutMap, checkoutMarker;
    
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', () => {
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }
            if (!cityLocation) {
                alert('Please search for a location first to place an order.');
                return;
            }
            
            locationModal.style.display = 'flex';
            const lat = cityLocation.lat;
            const lng = cityLocation.lng;
            
            if (!checkoutMap) {
                checkoutMap = L.map('deliveryMap').setView([lat, lng], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(checkoutMap);
                checkoutMarker = L.marker([lat, lng], {draggable: true}).addTo(checkoutMap);
            } else {
                checkoutMap.setView([lat, lng], 13);
                checkoutMarker.setLatLng([lat, lng]);
            }
            setTimeout(() => { checkoutMap.invalidateSize(); }, 300);
        });
    }

    if (closeMapBtn) closeMapBtn.addEventListener('click', () => { locationModal.style.display = 'none'; });
    
    if (confirmOrderBtn) confirmOrderBtn.addEventListener('click', async () => {
        const pos = checkoutMarker.getLatLng();
        const address = { lat: pos.lat, lng: pos.lng };
        
        const userId = 'U001';
        const restaurantId = cart[0].restaurant_id;

        const payload = {
            user_id: userId,
            restaurant_id: restaurantId,
            items: cart.map(i => ({id: i.id, name: i.name, price: i.price})),
            address: address,
            payment_method: document.querySelector('.method-btn.active img').alt.toLowerCase()
        };

        try {
            const resp = await fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data.success) {
                // Set the current order ID from the successful creation so tracking hooks onto it
                window.currentOrderId = data.order.id;
                alert(`Order confirmed! ID: ${data.order.id}`);
                locationModal.style.display = 'none';
                cart.length = 0;
                renderInvoice(); updateSummary();
                
                // Force SPA View Switch to Track Order
                document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
                const trackLink = Array.from(document.querySelectorAll('.sidebar-nav a')).find(l => l.getAttribute('data-target') === 'view-foodorder');
                if (trackLink) trackLink.classList.add('active');
                
                Object.values(views).forEach(v => { if (v) v.style.display = 'none'; });
                if (views['view-foodorder']) {
                    views['view-foodorder'].style.display = 'block';
                    if (liveMap) {
                        setTimeout(() => liveMap.invalidateSize(), 300);
                    }
                }
            } else {
                alert('Failed to create order: ' + data.error);
            }
        } catch (e) {
            console.error('Checkout error:', e);
            alert('Error during checkout');
        }
    });

    // --- Tracking Order Socket ---
    const socket = io.connect('http://localhost:5000');
    const trackEta = document.getElementById('trackEta');
    const trackOrderId = document.getElementById('trackOrderId');
    const timelineStatus = document.getElementById('timelineStatus');

    socket.onAny((eventName, msg) => {
        const activeOrderId = window.currentOrderId || 'FT-8527';
        if (eventName === `location_update_${activeOrderId}`) {
            
            // Hydrate Data Cards
            if (trackOrderId) trackOrderId.textContent = `#${msg.order_id}`;
            if (trackEta) {
                const remainingProgress = 100 - msg.progress;
                const dummyEtaMins = Math.max(1, Math.floor(remainingProgress * 0.3));
                trackEta.textContent = msg.arrived ? 'Arrived!' : `${dummyEtaMins} mins`;
            }

            // Hydrate Map Layer
            if (views['view-foodorder'].style.display !== 'none') {
                if (!liveMap && document.getElementById('liveTrackMap')) {
                    liveMap = L.map('liveTrackMap').setView([msg.location.lat, msg.location.lng], 16);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(liveMap);
                    
                    const bikeIcon = L.divIcon({
                        html: '<div style="font-size:24px; position:absolute; top:-12px; left:-12px; filter: drop-shadow(0px 2px 2px rgba(0,0,0,0.5));">🚲</div>',
                        className: 'dummy-bike-icon',
                    });
                    liveMarker = L.marker([msg.location.lat, msg.location.lng], {icon: bikeIcon}).addTo(liveMap);
                    routeLine = L.polyline([[msg.location.lat, msg.location.lng]], {color: '#f37154', weight: 4, opacity: 0.7}).addTo(liveMap);
                } else if (liveMap) {
                    liveMap.setView([msg.location.lat, msg.location.lng]);
                    liveMarker.setLatLng([msg.location.lat, msg.location.lng]);
                    routeLine.addLatLng([msg.location.lat, msg.location.lng]);
                }
            }

            // Hydrate Vertical Timeline
            if (timelineStatus && msg.steps) {
                const icons = ['📝', '👍', '🍳', '🚲', '📍'];
                timelineStatus.innerHTML = msg.steps.map((step, idx) => {
                    let sClass = step.status === 'completed' ? 'completed' : (step.status === 'active' ? 'active' : 'pending');
                    return `
                    <div class="v-step ${sClass}">
                        <span class="icon">${icons[idx] || '🔹'}</span>
                        <div class="det">
                            <h4>${step.title}</h4>
                            <p>${step.status === 'pending' ? 'Waiting...' : (step.status === 'active' ? 'In progress' : 'Done')}</p>
                        </div>
                    </div>
                    `;
                }).join('');
            }
            
            // Check Arrival Message Logic
            if (msg.arrived && !window.orderArrivedChecked) {
                window.orderArrivedChecked = true;
                
                const arrivalMsg = document.createElement('div');
                arrivalMsg.id = 'arrivalBanner';
                arrivalMsg.innerHTML = '<h3 style="color: #48bb78; text-align: center; padding: 20px; font-size: 1.2rem; animation: fadeIn 0.5s;">🎉 Order arrived safely!</h3>';
                
                timelineStatus.prepend(arrivalMsg);
                
                // Disappear / Reset after 2 minutes (120,000 ms)
                setTimeout(() => {
                    if (document.getElementById('arrivalBanner')) document.getElementById('arrivalBanner').remove();
                    timelineStatus.innerHTML = '<div class="v-step pending"><span class="icon">🕒</span><div class="det"><h4>Waiting for order</h4><p>Please place an order.</p></div></div>';
                    window.currentOrderId = null;
                    window.orderArrivedChecked = false;
                    if (trackEta) trackEta.textContent = '-- minutes';
                    if (trackOrderId) trackOrderId.textContent = '#-----';
                    if (liveMap) {
                        liveMap.remove();
                        liveMap = null;
                    }
                }, 120000);
            }
        }
    });

    // --- Feedback Logic ---
    const starSpans = document.querySelectorAll('#starRating span');
    let ratingValue = 5;
    starSpans.forEach(star => {
        star.addEventListener('click', (e) => {
            ratingValue = e.target.getAttribute('data-val');
            starSpans.forEach(s => s.classList.remove('active'));
            for(let i=0; i<ratingValue; i++) starSpans[i].classList.add('active');
        });
    });

    const submitFeedbackBtn = document.getElementById('submitFeedbackBtn');
    if (submitFeedbackBtn) submitFeedbackBtn.addEventListener('click', async () => {
        const text = document.getElementById('feedbackText').value;
        try {
            const resp = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: ratingValue, comments: text })
            });
            const data = await resp.json();
            if (data.success) {
                alert('Thank you for your feedback!');
                document.getElementById('feedbackText').value = '';
            }
        } catch(e) {
            console.error(e);
            alert('Could not submit feedback at this time.');
        }
    });

    // --- Order History Fetching ---
    async function loadHistory() {
        const grid = document.getElementById('historyGrid');
        if (!grid) return;
        grid.innerHTML = '<p>Loading...</p>';
        try {
            const resp = await fetch('/api/user/U001/orders?limit=3');
            const data = await resp.json();
            if (data.success) {
                if (data.orders.length === 0) {
                    grid.innerHTML = '<p>No past orders available.</p>';
                    return;
                }
                grid.innerHTML = data.orders.map(order => {
                    const d = new Date(order.times.ordered);
                    return `
                        <div class="history-card">
                            <h4>Order #${order.id}</h4>
                            <div class="date">${d.toLocaleDateString()} at ${d.toLocaleTimeString()}</div>
                            <div class="items">
                                ${order.items.map(i => i.name).join(', ')}
                            </div>
                            <div style="color: #48bb78; font-weight: bold;">Status: ${order.status.toUpperCase()}</div>
                            <div style="margin-top: 10px; font-size: 1.1rem; font-weight: 700;">₹${order.total_price}</div>
                        </div>
                    `;
                }).join('');
            }
        } catch(e) {
            console.error(e);
            grid.innerHTML = '<p>Error loading history.</p>';
        }
    }

    // Init Dash
    if(foodGrid) foodGrid.innerHTML = '<h3>Please search for a location to view restaurants!</h3>';
    renderInvoice();
    updateSummary();
});