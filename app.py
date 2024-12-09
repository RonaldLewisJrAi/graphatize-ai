from flask import Flask, render_template_string, session, redirect, url_for, request, jsonify
import stripe
import smtplib  # For email verification
import random  # To generate verification codes

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Stripe Configuration
stripe.api_key = "sk_test_Your_Secret_Key"  # Replace with your Stripe secret key
STRIPE_PRICE_ID = "price_Your_Price_ID"  # Replace with your Stripe price ID

# Dummy database for users and prompts
users = {}  # Example: {"username": {"password": "hash", "email": "email", "verified": False, "subscribed": False, "saved_prompts": []}}
verification_codes = {}  # Temporary storage for email verification codes

@app.route("/")
def home():
    logged_in = session.get("logged_in", False)
    subscribed = session.get("subscribed", False)
    username = session.get("username")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graphatize AI Art Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f9; }
            header { background: #333; color: white; padding: 10px; text-align: center; }
            .container { max-width: 900px; margin: 20px auto; background: white; padding: 20px; border-radius: 8px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .btn:disabled { background: #aaa; cursor: not-allowed; }
            .notice { color: red; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <header>
            <h1>Graphatize AI Art Generator</h1>
        </header>
        <div class="container">
            <h2>Create Your Art Prompt</h2>
            <form>
                <label for="category">Category:</label>
                <select id="category" name="category" {% if not subscribed %}disabled{% endif %}>
                    <option value="people">People</option>
                    <option value="animals">Animals</option>
                    <option value="vehicles">Vehicles</option>
                    <option value="environments">Environments</option>
                </select><br><br>
                <label for="number">Number of items:</label>
                <input type="number" id="number" name="number" min="1" max="100" {% if not subscribed %}disabled{% endif %}><br><br>
                <button class="btn" type="submit" {% if not subscribed %}disabled{% endif %}>Generate</button>
            </form>
            <p><a href="/saved">View Saved Prompts</a></p>
            {% if not logged_in %}
                <p class="notice">Please <a href="/login">log in</a> or <a href="/register">register</a> to use the generator.</p>
            {% elif not subscribed %}
                <p class="notice">Please <a href="/subscribe">subscribe</a> to unlock full functionality.</p>
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
        email = request.form.get("email")
        if username in users:
            return "User already exists. Please log in instead."
        verification_code = random.randint(100000, 999999)
        verification_codes[email] = verification_code
        # Send email (simplified for demonstration purposes)
        print(f"Verification code for {email}: {verification_code}")
        users[username] = {"password": password, "email": email, "verified": False, "subscribed": False, "saved_prompts": []}
        return redirect(url_for("verify_email"))
    return render_template_string("""
    <h1>Register</h1>
    <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br>
        <label>Password:</label><br>
        <input type="password" name="password" required><br>
        <label>Email:</label><br>
        <input type="email" name="email" required><br>
        <button type="submit">Register</button>
    </form>
    """)

@app.route("/verify_email", methods=["GET", "POST"])
def verify_email():
    if request.method == "POST":
        email = request.form.get("email")
        code = int(request.form.get("code"))
        if verification_codes.get(email) == code:
            for user in users.values():
                if user["email"] == email:
                    user["verified"] = True
                    return redirect(url_for("login"))
        return "Invalid code. Please try again."
    return render_template_string("""
    <h1>Verify Email</h1>
    <form method="POST">
        <label>Email:</label><br>
        <input type="email" name="email" required><br>
        <label>Verification Code:</label><br>
        <input type="number" name="code" required><br>
        <button type="submit">Verify</button>
    </form>
    """)

@app.route("/saved")
def saved():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    username = session["username"]
    saved_prompts = users[username]["saved_prompts"]
    return render_template_string("""
    <h1>Saved Prompts</h1>
    <ul>
        {% for prompt in saved_prompts %}
            <li>{{ prompt }}</li>
        {% endfor %}
    </ul>
    {% if len(saved_prompts) < 5 or session.get("subscribed") %}
        <form method="POST" action="/save_prompt">
            <label>New Prompt:</label><br>
            <input type="text" name="prompt" required><br>
            <button type="submit">Save Prompt</button>
        </form>
    {% else %}
        <p>You have reached the limit of 5 saved prompts. Upgrade to premium for unlimited saved prompts!</p>
    {% endif %}
    """)

@app.route("/save_prompt", methods=["POST"])
def save_prompt():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    username = session["username"]
    prompt = request.form.get("prompt")
    if len(users[username]["saved_prompts"]) < 5 or session.get("subscribed"):
        users[username]["saved_prompts"].append(prompt)
    return redirect(url_for("saved"))

# Include existing login, subscription, and logout routes
# Add your Stripe keys and ensure saved prompts work

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

