from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import random
from model import MockDB
import time
from geopy.distance import geodesic

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'foodtrack-secret-key'
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Explicitly allow API routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
db = MockDB()
print("Initial orders:", db.orders)  # Debug log

# Create initial order with specific ID
order_id = 'FT-8527'  # Hardcode the order ID to match frontend
db.create_order('U001', 'R001', [{'name': 'Margherita Pizza', 'price': 12.99}], '123 Main St, NY', 'credit', order_id=order_id)
print(f"Order created with ID {order_id}: {db.orders.get(order_id)}")  # Debug log to verify

# Add past delivered orders
past1 = db.create_order('U001', 'R002', [{'name': 'Classic Beef Taco', 'price': 120}], '123 Main St, NY', 'credit')
db.update_order_status(past1['id'], 'delivered')
past2 = db.create_order('U001', 'R003', [{'name': 'Butter Chicken', 'price': 350}], '123 Main St, NY', 'credit')
db.update_order_status(past2['id'], 'delivered')
past3 = db.create_order('U001', 'R004', [{'name': 'Classic Smash', 'price': 199}], '123 Main St, NY', 'paypal')
db.update_order_status(past3['id'], 'delivered')

# Driver simulation
def simulate_driver_movement():
    while True:
        for order_id in list(db.orders.keys()):
            order = db.get_order(order_id)
            if not order or order["status"] == "delivered":
                continue
            location_data = db.locations.get(order_id, {})
            if not location_data:
                continue
            current = location_data.get("current", order["tracking"]["start_location"])
            destination = location_data.get("destination", order["tracking"]["destination"])
            step_size = 0.0001 + random.random() * 0.0002
            direction_lat = destination["lat"] - current["lat"]
            direction_lng = destination["lng"] - current["lng"]
            magnitude = (direction_lat**2 + direction_lng**2)**0.5
            if magnitude > 0:
                step_lat = direction_lat / magnitude * step_size
                step_lng = direction_lng / magnitude * step_size
                new_lat = current["lat"] + step_lat
                new_lng = current["lng"] + step_lng
                if db.update_driver_location(order_id, new_lat, new_lng):
                    progress = order["tracking"]["progress"]
                    socketio.emit(f'location_update_{order_id}', {
                        'order_id': order_id,
                        'location': {'lat': new_lat, 'lng': new_lng},
                        'progress': progress,
                        'steps': order['steps']
                    })
                    distance_to_dest = geodesic((new_lat, new_lng), (destination["lat"], destination["lng"])).kilometers
                    if distance_to_dest < 0.05 and order["status"] != "delivered":
                        # Force final progress to 100%
                        db.orders[order_id]["tracking"]["progress"] = 100
                        db.update_order_status(order_id, "delivered")
                        
                        # Emit final completed event
                        socketio.emit(f'location_update_{order_id}', {
                            'order_id': order_id,
                            'location': {'lat': destination["lat"], 'lng': destination["lng"]},
                            'progress': 100,
                            'steps': db.get_order(order_id)['steps'],
                            'arrived': True
                        })
                        
                        db.add_chat_message(order_id, "bot", "Your order has been delivered! Enjoy your meal and earn 20 eco-points!")
                        db.award_eco_points(order["user_id"], 20, "Order delivered")
        time.sleep(1)

simulation_thread = threading.Thread(target=simulate_driver_movement)
simulation_thread.daemon = True
simulation_thread.start()

# Chatbot logic
def process_chatbot_message(message, order_id):
    message = message.lower().strip()
    order = db.get_order(order_id)
    if not order:
        return "Order not found. How can I assist you?", None

    user_id = order["user_id"]
    user = db.users.get(user_id, {})
    language = user.get("language", "en")

    greetings = {"en": "Hi", "hi": "नमस्ते", "es": "Hola"}
    greeting = greetings.get(language, "Hi")

    if "status" in message or "update" in message:
        steps = order["steps"]
        items_str = ", ".join([item.get("name", "Item") for item in order.get("items", [])])
        status_msg = f"{greeting}! Your order #{order_id} status:\n"
        for step in steps:
            title = step['title']
            status = step['status']
            time_str = step['time'][:16].replace("T", " ")
            
            if "Confirmed" in title:
                status_msg += f"- {title}: {status} (Items: {items_str}) at {time_str}\n"
            elif "Picked-up" in title or "Out for" in title or "On the way" in title:
                status_msg += f"- {title}: {status} (Driver collected) at {time_str}\n"
            elif "Near-by" in title or "Near" in title:
                status_msg += f"- {title}: {status} (Arriving in ~5 mins) at {time_str}\n"
            else:
                status_msg += f"- {title}: {status} at {time_str}\n"
        return status_msg, None

    elif "location" in message or "where" in message or "track" in message:
        loc = order["tracking"]["current_location"]
        progress = order["tracking"]["progress"]
        eta = int((100 - progress) / 100 * 20)
        return (f"{greeting}! Your driver is {progress}% to your location. ETA: {eta} mins.", 
                {"type": "location", "progress": progress, "eta": eta})

    elif "driver" in message or "call" in message or "contact" in message:
        driver = db.get_driver(order["driver_id"])
        return (f"{greeting}! Here are the details for your driver, {driver['name']}.", 
                {"type": "driver_card", "driver": driver})

    elif "waste" in message or "eco" in message or "green" in message:
        stats = db.get_user_waste_stats(user_id)
        if stats and stats["eco_packaging_count"] < stats["total_orders"]:
            return f"{greeting}! Tip: Choose eco-packaging next time to reduce waste. You’ve saved {stats['total_waste_reduction']}g so far!", None
        return f"{greeting}! Great job saving {stats['total_waste_reduction']}g of waste! Try composting leftovers.", None

    elif "modify" in message or "change" in message or "eco-packaging" in message:
        if db.modify_order(order_id, {"eco_packaging": True}):
            return f"{greeting}! Eco-packaging added to order #{order_id}. You earned 20 eco-points!", None
        return f"{greeting}! Sorry, modifications aren’t possible now. Status: {order['status']}.", None

    elif "offer" in message or "discount" in message or "promo" in message:
        offers = db.get_active_offers()
        if offers:
            offer = random.choice(offers)
            return (f"{greeting}! Here’s a special offer for you:",
                    {"type": "offer_card", "offer": offer})
        return f"{greeting}! No offers right now, check back later!", None

    elif "points" in message or "reward" in message:
        points = user.get("points", 0)
        return f"{greeting}! You have {points} eco-points. Redeem them for discounts or keep going green!", None

    elif "fun" in message or "fact" in message:
        facts = [
            "Did you know? A single pizza box can be recycled into 10 new ones!",
            "Fun fact: Sushi was originally a way to preserve fish with rice!",
            "Burgers were invented in the U.S. in the late 19th century!"
        ]
        return f"{greeting}! {random.choice(facts)}", None

    return f"{greeting}! I can help with status, tracking, driver info, tips, offers, points, or fun facts. What’s on your mind?", {"type": "quick_replies"}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = db.get_order(order_id)
    if order:
        return jsonify({"success": True, "order": order})
    print(f"Order not found: {order_id}")  # Debug log
    return jsonify({"error": "Order not found"}), 404

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    return jsonify({"success": True, "drivers": list(db.drivers.values())})

@app.route('/api/search', methods=['GET'])
def search_location():
    location = request.args.get('location', '').strip().lower()
    # Map valid locations (Bengaluru maps to Bangalore in db)
    valid_locations = {
        'delhi': 'Delhi', 
        'hyderabad': 'Hyderabad', 
        'mumbai': 'Mumbai', 
        'bangalore': 'Bangalore', 
        'bengaluru': 'Bangalore', 
        'chennai': 'Chennai'
    }
    
    if location not in valid_locations:
        return jsonify({
            "success": False, 
            "message": "Out of Service", 
            "restaurants": []
        })
    
    city = valid_locations[location]
    # Filter restaurants by city
    city_restaurants = [r for r in db.restaurants.values() if r.get('city') == city]
    return jsonify({
        "success": True, 
        "message": f"Found {len(city_restaurants)} restaurants in {city}", 
        "restaurants": city_restaurants,
        "city_location": db.restaurants[city_restaurants[0]["id"]]["location"] if city_restaurants else None
    })

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    return jsonify({"success": True, "restaurants": list(db.restaurants.values())})

@app.route('/api/chat/<order_id>', methods=['GET'])
def get_chat_history(order_id):
    chat_history = db.get_chat_history(order_id)
    print(f"Chat history retrieved for order {order_id}: {len(chat_history)} messages")  # Debug log
    return jsonify({"success": True, "messages": chat_history})

@app.route('/api/chat/<order_id>', methods=['POST'])
def send_chat_message(order_id):
    data = request.json
    print(f"Received chat request for {order_id}: {data}")  # Debug log
    if 'message' not in data or 'sender' not in data:
        print(f"Error: Invalid chat request for {order_id}: {data}")
        return jsonify({"error": "Message and sender required"}), 400
    msg = db.add_chat_message(order_id, data['sender'], data['message'])
    if msg:
        print(f"Emitting message for order {order_id}: {msg}")
        socketio.emit(f'chat_message_{order_id}', msg)
        if data['sender'] == 'user':
            response_text, metadata = process_chatbot_message(data['message'], order_id)
            bot_msg = db.add_chat_message(order_id, 'bot', response_text, metadata)
            print(f"Emitting bot response for order {order_id}: {bot_msg}")
            # Emulate typing delay
            time.sleep(1.5)
            socketio.emit(f'chat_message_{order_id}', bot_msg)
        return jsonify({"success": True, "message": msg})
    print(f"Failed to add message for order {order_id} - Order not found")
    return jsonify({"error": "Failed to add message"}), 404

@app.route('/api/offers', methods=['GET'])
def get_offers():
    offers = db.get_active_offers()
    print(f"Retrieved {len(offers)} active offers")  # Debug log
    return jsonify({"success": True, "offers": offers})

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    required_fields = ['user_id', 'restaurant_id', 'items', 'address', 'payment_method']
    if not all(field in data for field in required_fields):
        print("Error: Missing required fields in order request")  # Debug log
        return jsonify({"error": "Missing required fields"}), 400
    order = db.create_order(data['user_id'], data['restaurant_id'], data['items'], data['address'], data['payment_method'])
    socketio.emit(f'points_update_{data["user_id"]}', {'points': db.users[data["user_id"]]["points"], 'reason': 'Order placed'})
    print(f"Order created: {order['id']}")  # Debug log
    print("Orders after creation:", db.orders.keys())  # Debug log
    return jsonify({"success": True, "order": order}), 201

@app.route('/api/user/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    limit = int(request.args.get('limit', 3))
    user_orders = [o for o in db.orders.values() if o['user_id'] == user_id]
    # Sort by creation time (descending), take last `limit`
    user_orders.sort(key=lambda x: x['times']['ordered'], reverse=True)
    return jsonify({"success": True, "orders": user_orders[:limit]})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    print(f"Feedback received: {data}")
    return jsonify({"success": True, "message": "Feedback submitted successfully!"}), 200

@socketio.on('connect')
def handle_connect():
    print("Client connected to Socket.IO")

@app.route('/payment-success')
def payment_success():
    return render_template('payment_success.html')

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected from Socket.IO")

if __name__ == '__main__':
    print("Starting Flask server with Socket.IO...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)