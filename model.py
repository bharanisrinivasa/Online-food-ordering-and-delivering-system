import json
import copy
from datetime import datetime, timedelta
import random
from geopy.distance import geodesic
import time

class MockDB:
    def __init__(self):
        self.orders = {}
        self.drivers = {}
        self.users = {}
        self.offers = {}
        self.waste_stats = {}
        self.locations = {}
        self.chat_messages = {}
        self.eco_points = {}
        self.restaurants = {}
        
        self._initialize_data()

    def _initialize_data(self):
        self._initialize_drivers()
        self._initialize_offers()
        self._initialize_users()
        self._initialize_restaurants()

    def _initialize_drivers(self):
        drivers = [
            {"id": "D001", "name": "James Wilson", "photo": "james_wilson.jpg", "rating": 4.92, "phone": "+1-555-123-4567", "vehicle": "Honda Civic", "licensePlate": "ABC123", "status": "active"},
            {"id": "D002", "name": "Sarah Johnson", "photo": "sarah_johnson.jpg", "rating": 4.85, "phone": "+1-555-234-5678", "vehicle": "Toyota Prius", "licensePlate": "XYZ789", "status": "active"},
            {"id": "D003", "name": "Amit Patel", "photo": "amit_patel.jpg", "rating": 4.78, "phone": "+1-555-345-6789", "vehicle": "Tesla Model 3", "licensePlate": "TESLA1", "status": "active"},
            {"id": "D004", "name": "Maria Gomez", "photo": "maria_gomez.jpg", "rating": 4.95, "phone": "+1-555-456-7890", "vehicle": "Ford Mustang", "licensePlate": "MUST22", "status": "active"}
        ]
        for driver in drivers:
            self.drivers[driver["id"]] = driver

    def _initialize_offers(self):
        offers = [
            {"id": "O001", "title": "50% Off First Order", "description": "New users get half off!", "tag": "Limited Time", "image": "offer1.jpg", "expires": (datetime.now() + timedelta(days=3)).isoformat(), "code": "FIRST50", "status": "active"},
            {"id": "O002", "title": "Free Delivery ₹500+", "description": "Free delivery this weekend!", "tag": "Weekend Special", "image": "offer2.jpg", "expires": (datetime.now() + timedelta(days=7)).isoformat(), "code": "FREEDEL500", "status": "active"},
            {"id": "O003", "title": "20% Off Eco-Packaging", "description": "Choose green packaging!", "tag": "Eco-Friendly", "image": "offer3.jpg", "expires": (datetime.now() + timedelta(days=30)).isoformat(), "code": "ECO20", "status": "active"},
            {"id": "O004", "title": "Buy 1 Get 1 Free", "description": "On select pizzas!", "tag": "Pizza Lovers", "image": "offer4.jpg", "expires": (datetime.now() + timedelta(days=5)).isoformat(), "code": "BOGO", "status": "active"}
        ]
        for offer in offers:
            self.offers[offer["id"]] = offer

    def _initialize_users(self):
        users = [
            {"id": "U001", "name": "John Doe", "email": "john@example.com", "points": 150, "language": "en", "order_history": ["FT-8527"]},
            {"id": "U002", "name": "Priya Sharma", "email": "priya@example.com", "points": 80, "language": "hi", "order_history": []},
            {"id": "U003", "name": "Carlos Rivera", "email": "carlos@example.com", "points": 200, "language": "es", "order_history": []}
        ]
        for user in users:
            self.users[user["id"]] = user

    def _initialize_restaurants(self):
        base_templates = [
            {
                "name": "Pizza Palace",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300",
                "menu": [
                    {"name": "Margherita Pizza", "price": 299, "description": "Classic delight with 100% real mozzarella cheese", "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=300"},
                    {"name": "Pepperoni Pizza", "price": 399, "description": "Double pepperoni, double fun", "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=300"},
                    {"name": "Veggie Supreme", "price": 349, "description": "Loaded with onions, crisp capsicum, and fresh tomatoes", "image": "https://images.unsplash.com/photo-1528137871618-79d2761e3fd5?w=300"},
                    {"name": "BBQ Chicken Pizza", "price": 449, "description": "Tangy BBQ sauce topped with grilled chicken", "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300"},
                    {"name": "Garlic Breadsticks", "price": 149, "description": "Freshly baked and brushed with garlic butter", "image": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=300"}
                ]
            },
            {
                "name": "Taco Fiesta",
                "image": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=300",
                "menu": [
                    {"name": "Classic Beef Taco", "price": 120, "description": "Seasoned ground beef in a crunchy shell", "image": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=300"},
                    {"name": "Spicy Chicken Burrito", "price": 250, "description": "Grilled chicken, rice, beans, and fiery salsa", "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=300"},
                    {"name": "Cheese Quesadilla", "price": 199, "description": "Melted cheese blend folded in a warm tortilla", "image": "https://images.unsplash.com/photo-1618040996337-df9abfe4eb7d?w=300"},
                    {"name": "Loaded Nachos", "price": 280, "description": "Tortilla chips smothered in queso, jalapeños, and beef", "image": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=300"},
                    {"name": "Churros", "price": 140, "description": "Crispy fried dough dusted with cinnamon sugar", "image": "https://images.unsplash.com/photo-1624371414361-e670edf4898d?w=300"}
                ]
            },
            {
                "name": "Curry House",
                "image": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=300",
                "menu": [
                    {"name": "Butter Chicken", "price": 350, "description": "Tender chicken simmered in a creamy tomato sauce", "image": "https://images.unsplash.com/photo-1603894584373-5ac82b6ae398?w=300"},
                    {"name": "Paneer Tikka Masala", "price": 320, "description": "Grilled cottage cheese cubes in a spiced gravy", "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=300"},
                    {"name": "Garlic Naan", "price": 60, "description": "Traditional flatbread baked with fresh garlic", "image": "https://images.unsplash.com/photo-1600850056064-a8b380df8395?w=300"},
                    {"name": "Vegetable Biryani", "price": 250, "description": "Aromatic basmati rice cooked with mixed veggies and spices", "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"},
                    {"name": "Samosa Chaat", "price": 120, "description": "Crushed samosas topped with yogurt, tamarind, and mint chutney", "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300"}
                ]
            },
            {
                "name": "Burger Barn",
                "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300",
                "menu": [
                    {"name": "The Classic Smash", "price": 199, "description": "A single smashed patty, American cheese, lettuce, and tomato", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300"},
                    {"name": "Double Bacon Bacon", "price": 349, "description": "Two patties stacked high with crispy bacon and cheese", "image": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=300"},
                    {"name": "Spicy Black Bean Burger", "price": 249, "description": "A hearty vegetarian black bean patty with chipotle mayo", "image": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=300"},
                    {"name": "Crispy Onion Rings", "price": 149, "description": "Golden, crunchy rings of sweet onion", "image": "https://images.unsplash.com/photo-1639024470081-ce0eb1bd4418?w=300"},
                    {"name": "Oreo Milkshake", "price": 180, "description": "Thick hand-spun shake packed with Oreo crumbles", "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=300"}
                ]
            },
            {
                "name": "Dosa Diner",
                "image": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?w=300",
                "menu": [
                    {"name": "Masala Dosa", "price": 120, "description": "Crispy golden crepe stuffed with potato masala", "image": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?w=300"},
                    {"name": "Idli Sambar", "price": 80, "description": "Steamed rice cakes with lentil soup", "image": "https://images.unsplash.com/photo-1627440366663-87bb16186eb5?w=300"},
                    {"name": "Medu Vada", "price": 90, "description": "Crispy lentil doughnuts", "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300"},
                    {"name": "Filter Coffee", "price": 50, "description": "Traditional South Indian strong coffee", "image": "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=300"},
                    {"name": "Kesari Bath", "price": 100, "description": "Sweet semolina dessert with cashews", "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"}
                ]
            }
        ]

        cities = {
            "Delhi": {"lat": 28.6120, "lng": 77.2080},
            "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
            "Mumbai": {"lat": 19.0760, "lng": 72.8777},
            "Bangalore": {"lat": 12.9716, "lng": 77.5946},
            "Chennai": {"lat": 13.0827, "lng": 80.2707}
        }

        self.restaurants = {}
        r_id_counter = 1

        for i, (city, loc) in enumerate(cities.items()):
            # Rotate out 4 distinct templates for this city cleanly
            selected_templates = [base_templates[(i + offset) % len(base_templates)] for offset in range(4)]
            
            for tmpl in selected_templates:
                new_rest = copy.deepcopy(tmpl)
                r_id = f"R{r_id_counter:03d}"
                new_rest["id"] = r_id
                new_rest["city"] = city
                new_rest["location"] = loc
                
                # Assign unique IDs to menu items
                for m_idx, item in enumerate(new_rest["menu"]):
                    item["id"] = f"{r_id}_m{m_idx + 1}"
                
                self.restaurants[r_id] = new_rest
                r_id_counter += 1

    def create_order(self, user_id, restaurant_id, items, address, payment_method, order_id=None):
        if not order_id:
            order_id = f"FT-{random.randint(1000, 9999)}"  # Dynamic order ID
        driver_id = random.choice(list(self.drivers.keys()))
        driver = self.drivers[driver_id]
        
        order_time = datetime.now()
        prep_time = order_time + timedelta(minutes=10)
        pickup_time = prep_time + timedelta(minutes=5)
        delivery_time = pickup_time + timedelta(minutes=15)
        
        start_location = self.restaurants[restaurant_id]["location"].copy()
        destination = {"lat": start_location["lat"] + (random.random() - 0.5) * 0.02, "lng": start_location["lng"] + (random.random() - 0.5) * 0.02}
        current_location = start_location.copy()
        
        order = {
            "id": order_id,
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "driver_id": driver_id,
            "items": items,
            "address": address,
            "payment_method": payment_method,
            "status": "confirmed",
            "times": {
                "ordered": order_time.isoformat(),
                "preparation": prep_time.isoformat(),
                "pickup": pickup_time.isoformat(),
                "estimated_delivery": delivery_time.isoformat()
            },
            "total_price": round(sum(item.get("price", 0) for item in items), 2),
            "tracking": {
                "start_location": start_location,
                "current_location": current_location,
                "destination": destination,
                "progress": 0
            },
            "steps": []
        }
        order["steps"] = self._generate_timeline(order, 0)
        self.orders[order_id] = order
        self.locations[order_id] = {"start": start_location, "current": current_location, "destination": destination, "last_updated": time.time()}
        self.chat_messages[order_id] = [
            {"sender": "bot", "message": f"Hi! Your order #{order_id} from {self.restaurants[restaurant_id]['name']} is confirmed.", "timestamp": order_time.isoformat()}
        ]
        self.waste_stats[order_id] = {
            "packaging_type": "standard",
            "eco_packaging_opted": False,
            "estimated_waste_reduction": 0,
            "carbon_footprint": random.randint(100, 300),
            "tips_followed": [],
            "items_wasted": 0
        }
        self.award_eco_points(user_id, 10, "Order placed")
        if user_id in self.users:
            self.users[user_id]["order_history"].append(order_id)
        return order

    def award_eco_points(self, user_id, points, reason):
        if user_id in self.users:
            self.users[user_id]["points"] = self.users[user_id].get("points", 0) + points
            return True
        return False

    def update_driver_location(self, order_id, lat, lng):
        if order_id in self.orders and order_id in self.locations:
            self.locations[order_id]["current"] = {"lat": lat, "lng": lng}
            self.locations[order_id]["last_updated"] = time.time()
            start = self.locations[order_id]["start"]
            dest = self.locations[order_id]["destination"]
            curr = self.locations[order_id]["current"]
            start_to_dest = geodesic((start["lat"], start["lng"]), (dest["lat"], dest["lng"])).kilometers
            curr_to_dest = geodesic((curr["lat"], curr["lng"]), (dest["lat"], dest["lng"])).kilometers
            if start_to_dest > 0:
                progress = min(100, max(0, ((start_to_dest - curr_to_dest) / start_to_dest) * 100))
                self.orders[order_id]["tracking"]["progress"] = round(progress, 1)
                self.orders[order_id]["tracking"]["current_location"] = curr
                return True
        return False

    def update_order_status(self, order_id, status):
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            steps_map = {"confirmed": 0, "preparing": 1, "out_for_delivery": 2, "nearby": 3, "delivered": 4}
            if status in steps_map:
                step_index = steps_map[status]
                for i in range(step_index + 1):
                    self.orders[order_id]["steps"][i]["status"] = "completed"
                if step_index < 4:
                    self.orders[order_id]["steps"][step_index + 1]["status"] = "active"
            if status == "delivered":
                self.award_eco_points(self.orders[order_id]["user_id"], 20, "Order delivered")
            return True
        return False

    def _generate_timeline(self, order, progress):
        def get_status(start, end):
            if progress >= end: return "completed"
            if progress > start: return "active"
            return "pending"
            
        return [
            {"status": "completed", "title": "Order Confirmed", "time": order["times"]["ordered"]},
            {"status": get_status(0, 30), "title": "Picked-up", "time": order["times"]["ordered"]},
            {"status": get_status(30, 70), "title": "On the way", "time": order["times"]["ordered"]},
            {"status": get_status(70, 99), "title": "Near-by you", "time": order["times"]["estimated_delivery"]},
            {"status": "completed" if progress == 100 else "pending", "title": "Arrived", "time": order["times"]["estimated_delivery"]}
        ]

    def get_order(self, order_id):
        order = self.orders.get(order_id)
        if order:
            progress = order.get("tracking", {}).get("progress", 0)
            order["steps"] = self._generate_timeline(order, progress)
        return order

    def get_driver(self, driver_id):
        return self.drivers.get(driver_id)

    def add_chat_message(self, order_id, sender, message, metadata=None):
        if order_id in self.chat_messages:
            msg = {"sender": sender, "message": message, "timestamp": datetime.now().isoformat()}
            if metadata:
                msg["metadata"] = metadata
            self.chat_messages[order_id].append(msg)
            return msg
        return None

    def get_chat_history(self, order_id):
        return self.chat_messages.get(order_id, [])

    def get_active_offers(self):
        now = datetime.now().isoformat()
        return [offer for offer in self.offers.values() if offer["status"] == "active" and offer["expires"] > now]

    def modify_order(self, order_id, modification):
        if order_id in self.orders and self.orders[order_id]["status"] in ["confirmed", "preparing"]:
            if "eco_packaging" in modification and modification["eco_packaging"]:
                self.waste_stats[order_id]["eco_packaging_opted"] = True
                self.waste_stats[order_id]["estimated_waste_reduction"] += 50
                self.award_eco_points(self.orders[order_id]["user_id"], 20, "Chose eco-packaging")
                return True
        return False

    def get_user_waste_stats(self, user_id):
        if user_id not in self.users:
            return None
        user_orders = [order for order in self.orders.values() if order["user_id"] == user_id]
        total_waste_reduction = sum(self.waste_stats[o["id"]]["estimated_waste_reduction"] for o in user_orders if o["id"] in self.waste_stats)
        eco_packaging_count = sum(1 for o in user_orders if self.waste_stats[o["id"]]["eco_packaging_opted"])
        return {
            "total_orders": len(user_orders),
            "eco_packaging_count": eco_packaging_count,
            "total_waste_reduction": total_waste_reduction
        }