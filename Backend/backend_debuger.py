from flask import Flask, jsonify

# Create a brand new Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "ROOT WORKS!"

@app.route('/api/health')
def health():
    return "HEALTH WORKS!"

@app.route('/api/test')
def test():
    return "TEST WORKS!"

@app.route('/api/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(f"{','.join(rule.methods)} {rule}")
    return jsonify({"routes": routes})

if __name__ == '__main__':
    print("🚀 STARTING DEBUG SERVER ON PORT 5003")
    print("📍 Test these URLs:")
    print("   http://localhost:5003/")
    print("   http://localhost:5003/api/health") 
    print("   http://localhost:5003/api/test")
    print("   http://localhost:5003/api/debug/routes")
    print("=" * 50)
    app.run(debug=True, port=5003, host='0.0.0.0')