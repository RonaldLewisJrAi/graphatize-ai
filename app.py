from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Dummy user database
users = {}
saved_prompts = {}

# Example categories and options
categories = {
    "people": {
        "attributes": ["race", "sex", "age", "height", "hairstyle", "hair color", "eye color", "facial structure"],
        "subtle_features": ["freckles", "piercings", "scars"]
    },
    "animals": ["species", "breed", "size", "habitat", "color patterns"],
    "vehicles": ["year", "model", "type", "style"],
    "architecture": ["style", "region", "material"],
    "fashion": ["type", "fabric", "pattern", "culture"]
}

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Art Prompt Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
            header { background: #333; color: white; padding: 10px; text-align: center; }
            .container { max-width: 800px; margin: 20px auto; padding: 20px; }
            .btn { background: #007bff; color: white; padding: 10px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h1>AI Art Prompt Generator</h1>
        </header>
        <div class="container">
            <h2>Create Your Prompt</h2>
            <form action="/generate" method="POST">
                <label for="category">Category:</label>
                <select name="category" required>
                    {% for category in categories %}
                        <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                </select><br><br>
                <label for="details">Details (comma-separated):</label>
                <input type="text" name="details" placeholder="e.g., race, age"><br><br>
                <label for="number">Number of items:</label>
                <input type="number" name="number" min="1" max="100" value="1"><br><br>
                <button class="btn" type="submit">Generate Prompt</button>
            </form>
            <hr>
            <h3>Saved Prompts</h3>
            <ul>
                {% for prompt in saved_prompts %}
                    <li>{{ prompt }}</li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    """, categories=categories.keys(), saved_prompts=saved_prompts.get(session.get("username"), []))

@app.route("/generate", methods=["POST"])
def generate():
    category = request.form.get("category")
    details = request.form.get("details", "").split(",")
    number = request.form.get("number", 1)

    prompt = f"Generate {number} {category} with details: {', '.join(details)}"
    if session.get("username"):
        saved_prompts.setdefault(session["username"], []).append(prompt)
    return jsonify({"prompt": prompt})

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users[username] = {"password": password}
        session["username"] = username
        return "Registered successfully! <a href='/'>Go to Home</a>"
    return render_template_string("""
    <h1>Register</h1>
    <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br>
        <label>Password:</label><br>
        <input type="password" name="password" required><br>
        <button type="submit">Register</button>
    </form>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if users.get(username, {}).get("password") == password:
            session["username"] = username
            return "Logged in successfully! <a href='/'>Go to Home</a>"
        return "Invalid credentials."
    return render_template_string("""
    <h1>Login</h1>
    <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br>
        <label>Password:</label><br>
        <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
