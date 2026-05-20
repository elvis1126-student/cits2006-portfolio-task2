from flask import Flask, jsonify, redirect, session
import random
import threading
import time
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # session signing

TTL_SECONDS = 60
MAX_ACTIVE_ROUTES = 3
ROTATION_INTERVAL = 20

routing_table = {}
current_route = None
route_table_locking = threading.Lock()
old_routes = set()

def generate_route():
    # MTD idea, generating new endpoint
    return f"/admin_{random.randint(1000, 9999)}"


def shuffle_routes():
    global current_route

    while True:
        time.sleep(ROTATION_INTERVAL)

        new_route = generate_route()
        expiry_time = datetime.now() + timedelta(seconds=TTL_SECONDS)

        # aviod unrelated thread accessing and update the routing table
        with route_table_locking:
            old_routes.add(new_route)
            routing_table[new_route] = {
                "service": "admin_panel",
                "expires": expiry_time
            }
            current_route = new_route
            print(f"new route generated: {new_route}")
            cleanup_routes()


def cleanup_routes():
    # check and removed unnecessary routes

    # get current time
    now = datetime.now()

    expired = []
    for route, info in routing_table.items():
        if info["expires"] < now: # check expeire 
            expired.append(route)

    # removing expired
    for route in expired:
        print(f"removing expired route: {route}")
        old_routes.add(route)
        del routing_table[route]

    print(routing_table)
    # removing extra
    while len(routing_table) > MAX_ACTIVE_ROUTES:
        oldest_route = min(routing_table, key=lambda r: routing_table[r]["expires"])
        print(f"removing old route: {oldest_route}")
        old_routes.add(oldest_route)
        del routing_table[oldest_route]
    print("old:",old_routes)


def is_route_valid(route):
    # check the endpoint is vaild or not
    route_info = routing_table.get(route)
    if route_info is not None and route_info["expires"] >= datetime.now():
        return route_info
    return False


@app.route('/latest')
def latest_route():
    with route_table_locking:
        route = current_route

    if route is None:
        return jsonify({"error": "No active route available"}), 503

    return jsonify({"latest_endpoint": route})


@app.route('/<path:endpoint>')
def access_endpoint(endpoint):
    route = f"/{endpoint}"

    if route == "/latest":
        return latest_route()

    # aviod unrelated thread accessing and check user accessing endpoint is valid or not
    with route_table_locking:
        valid_route = is_route_valid(route)
        latest = current_route

    if valid_route:
        # keeping authenticated user alive
        session["authenticated"] = True
        route_info = routing_table[route]
        return jsonify({
            "status": "success",
            "message": "Connected to service",
            "expires": route_info["expires"].strftime('%H:%M:%S')
        })

    # check user is perviuosly authernticated 
    if session.get("authenticated") and route in old_routes:
        # redirect to new route
        return redirect(latest, code=302)

    # 404
    return jsonify({
        "status": "denied",
        "message": "Invalid access point"
    }), 404


def application():
    global current_route

    new_route = generate_route()
     
    # aviod unrelated thread accessing and update the routing table
    with route_table_locking:
        old_routes.add(new_route)
        routing_table[new_route] = {
            "service": "admin_panel",
            "expires": datetime.now() + timedelta(seconds=TTL_SECONDS)
        }
        current_route = new_route
        cleanup_routes()

    print(f"active route: {new_route}")


if __name__ == "__main__":
    application()

    change_endpoint_thread = threading.Thread(target=shuffle_routes, daemon=True)
    change_endpoint_thread.start()

    app.run(debug=True)