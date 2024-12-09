from flask import Flask, render_template_string, request, session, redirect, url_for
import stripe

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Stripe configuration (your shared keys)
stripe.api_key = "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"  # Your Stripe secret key
STRIPE_PRICE_ID = "prctbl_1QTunJPJfMWwkhDQNsSy4PPD"  # Your Stripe price ID for the subscription

# Example user database
users = {}  # Format: {"username": {"password": "password", "premium": False, "stripe_customer_id": None}}

@app.route("/")
def home():
    logged_in = session.get("logged_in", False)
    username = session.get("username")
    user = users.get(username) if username else None
    premium = user["premium"] if user else False

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graphatize AI Art Prompt Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f9; }
            header { background: #333; color: white; padding: 20px; text-align: center; }
            .container { max-width: 900px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <header>
            <h1>Graphatize AI Art Prompt Generator</h1>
        </header>
        <div class="container">
            {% if logged_in %}
                <h2>Welcome, {{ username }}</h2>
                <p>{{ "Premium User" if premium else "Free User" }}</p>
                {% if not premium %}
                    <a href="/subscribe"><button class="btn">Upgrade to Premium</button></a>
                {% else %}
                    <a href="/dashboard"><button class="btn">Manage Subscription</button></a>
                {% endif %}
                <hr>
                <h3>Create Your Prompt</h3>
                <form action="/generate" method="POST">
                    <label for="category">Category:</label>
                    <input type="text" name="category" placeholder="e.g., People, Animals" required><br><br>
                    <label for="details">Details:</label>
                    <input type="text" name="details" placeholder="e.g., Race, Age"><br><br>
                    <label for="number">Number of items:</label>
                    <input type="number" name="number" min="1" max="100" value="1"><br><br>
                    <button type="submit" class="btn">Generate</button>
                </form>
                <hr>
                <h4>Generated Prompt:</h4>
                <p>{{ session.get("generated_prompt", "Your prompt will appear here.") }}</p>
            {% else %}
                <p>Please <a href="/login">log in</a> or <a href="/register">register</a> to use the generator.</p>
            {% endif %}
        </div>
    </body>
    </html>
    """, logged_in=logged_in, username=username, premium=premium)

@app.route("/subscribe")
def subscribe():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    user = users[username]

    # Create a Stripe Checkout Session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": STRIPE_PRICE_ID,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=url_for("subscription_success", _external=True),
        cancel_url=url_for("home", _external=True),
        customer_email=user["stripe_customer_id"] if user["stripe_customer_id"] else None
    )
    return redirect(checkout_session.url)

@app.route("/subscription_success")
def subscription_success():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    user = users[username]

    # Mark the user as premium
    user["premium"] = True
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session["username"]
    user = users[username]

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Subscription Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f9; }
            header { background: #333; color: white; padding: 20px; text-align: center; }
            .container { max-width: 900px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <header>
            <h1>Subscription Dashboard</h1>
        </header>
        <div class="container">
            <h2>Welcome, {{ username }}</h2>
            <p>Status: {{ "Premium User" if user["premium"] else "Free User" }}</p>
            <hr>
            <p>Manage your subscription through Stripe.</p>
            <a href="/subscribe"><button class="btn">Upgrade or Update Billing</button></a>
        </div>
    </body>
    </html>
    """, username=username, user=user)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users[username] = {"password": password, "premium": False, "stripe_customer_id": None}
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for("home"))
    return render_template_string("""
    <h1>Register</h1>
    <form method="POST">
        <label>Username:</label>
        <input type="text" name="username" required><br>
        <label>Password:</label>
        <input type="password" name="password" required><br>
        <button type="submit">Register</button>
    </form>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username]["password"] == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid credentials."
    return render_template_string("""
    <h1>Login</h1>
    <form method="POST">
        <label>Username:</label>
        <input type="text" name="username" required><br>
        <label>Password:</label>
        <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
