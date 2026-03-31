# Online Food Ordering and Delivery System 🍕🚴

A premium, full-stack Single Page Application (SPA) designed to simulate an end-to-end food ordering and delivery workflow. Built with a responsive frontend dashboard and a robust Python backend featuring real-time socket delivery tracking via Leaflet Maps.

## ✨ Key Features
- **Dynamic SPA Routing**: Instantly fluid transitions between Dashboard, Order Tracking, History, and Feedback tabs without page reloads.
- **Location-Based Restaurant Search**: Search specific cities to dynamically render available menus and local restaurants.
- **Live Order Delivery Tracking**: Leverages `Socket.IO` and `Leaflet.js` to draw animated delivery routes mapping your dummy driver's real-time trajectory towards your house.
- **Interactive Map Checkout**: Place your order dynamically by dragging a pin on a live map to confirm exact coordinate destinations.
- **Smart Eco-Chatbot**: A floating helper bot integrated with quick-reply scripts to assist with simulated support and tracking questions.
- **Order History & Feedback**: Cleanly interfaces with backend APIs to render mock order history cards and accept 1-5 star user reviews.

## 🛠️ Technology Stack
- **Frontend Engine**: Vanilla HTML5, CSS3, JavaScript (ES6+).
- **Interactive Mapping**: Leaflet.js
- **Real-Time Websockets**: Socket.IO
- **Backend Architecture**: Python 3, Flask framework.
- **Data Layer**: Custom in-memory `MockDB` structure generating lifelike user, city, layout, and localized delivery histories.

## 🚀 Getting Started

### Prerequisites
Make sure you have **[Python 3.x](https://www.python.org/)** installed on your system.

### Build Instructions
1. Clone the repository:
```bash
git clone https://github.com/bharanisrinivasa/Online-food-ordering-and-delivering-system.git
cd Online-food-ordering-and-delivering-system
```
2. Create and activate a Virtual Environment:
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On MacOS/Linux
source env/bin/activate
```
3. Install the required Python dependencies:
> **Note:** The core dependencies include `Flask`, `Flask-SocketIO`, and `Geopy`.
```bash
pip install -r requirements.txt
```

### Launching the Application
Launch the simulated backend server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/` to explore the beautiful dashboard layout! Try placing an order and watching the active 🚚 progress map tracking function in real time.
