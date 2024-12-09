from flask import Flask, render_template_string, session, redirect, url_for, request, jsonify
import stripe

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Stripe Configuration
stripe.api_key = "sk_test_Your_Secret_Key"  # Replace with your Stripe secret key
STRIPE_PRICE_ID = "price_Your_Price_ID"  # Replace with your Stripe price ID

# Dummy user database (in-memory, for simplicity)
users = {}

@app.route("/")
def home():
    logged_in = session.get("logged_in", False)
    subscribed = session.get("subscribed", False)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Graphatize AI Art Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f9; }
            header { background: #333; color: white; padding: 10px 20px; text-align: center; }
            .container { max-width: 900px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
            .btn:disabled { background: #aaa; cursor: not-allowed; }
            .notice { color: red; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <header>
            <h1>Graphatize AI Art Generator</h1>
        </header>
        <div class="container">
            <h2>Generate Your Art Prompt</h2>
            <p>Select your options and generate your custom art prompt:</p>
            <form>
                <label for="category">Category:</label>
                <select id="category" name="category" {% if not subscribed %}disabled{% endif %}>
                    <option value="people">People</option>
                    <option value="animals">Animals</option>
                    <option value="vehicles">Vehicles</option>
                    <option value="environments">Environments</option>
                </select><br><br>
                <button class="btn" type="button" {% if not subscribed %}disabled{% endif %}>Generate Prompt</button>
            </form>
            {% if not logged_in %}
                <p class="notice">Please <a href="/login">log in</a> or <a href="/register">register</a> to use the generator.</p>
            {% elif not subscribed %}
                <p class="notice">Please <a href="/subscribe">subscribe</a> to enable the generator.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """, logged_in=logged_in, subscribed=subscribed)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return "User already exists. Please log in instead."
        users[username] = {"password": password, "subscribed": False}
        return redirect(url_for("login"))
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
        user = users.get(username)
        if user and user["password"] == password:
            session["logged_in"] = True
            session["username"] = username
            session["subscribed"] = user["subscribed"]
            return redirect(url_for("home"))
        return "Invalid credentials. Please try again."
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

@app.route("/subscribe")
def subscribe():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    username = session["username"]

    # Redirect user to Stripe checkout
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=url_for("subscription_success", _external=True),
        cancel_url=url_for("home", _external=True),
    )
    return redirect(checkout_session.url)

@app.route("/subscription_success")
def subscription_success():
    username = session.get("username")
    if username:
        users[username]["subscribed"] = True
        session["subscribed"] = True
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
