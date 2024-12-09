from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Example categories with subcategories
categories = {
    "people": {
        "subcategories": ["race", "sex", "age", "height", "hairstyle", "hair color", "eye color", "facial structure"],
        "details": ["freckles", "piercings", "scars"]
    },
    "animals": {
        "subcategories": ["species", "breed", "size", "habitat", "color patterns"]
    },
    "vehicles": {
        "subcategories": ["year", "model", "type", "style"]
    },
    "architecture": {
        "subcategories": ["style", "region", "material"]
    },
    "fashion": {
        "subcategories": ["type", "fabric", "pattern", "culture"]
    }
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
            .generated-prompt { margin-top: 20px; padding: 10px; background: #f4f4f9; border: 1px solid #ccc; }
            .copy-icon { cursor: pointer; color: #007bff; font-weight: bold; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 5px 0; }
        </style>
        <script>
            function updatePrompt() {
                const category = document.querySelector('select[name="category"]').value;
                const subcategories = document.querySelectorAll('input[name="subcategory"]:checked');
                const number = document.querySelector('input[name="number"]').value;

                let selectedSubcategories = [];
                subcategories.forEach((checkbox) => selectedSubcategories.push(checkbox.value));

                const prompt = `Generate ${number} ${category} with: ${selectedSubcategories.join(", ")}`;
                document.getElementById("generated-prompt").innerText = prompt;
            }

            function copyToClipboard() {
                const promptText = document.getElementById("generated-prompt").innerText;
                navigator.clipboard.writeText(promptText).then(() => {
                    alert("Prompt copied to clipboard!");
                });
            }
        </script>
    </head>
    <body>
        <header>
            <h1>AI Art Prompt Generator</h1>
        </header>
        <div class="container">
            <h2>Create Your Prompt</h2>
            <form>
                <label for="category">Category:</label>
                <select name="category" onchange="updatePrompt()">
                    {% for category in categories %}
                        <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                </select><br><br>
                <label>Subcategories:</label>
                <ul>
                    {% for subcategory in categories["people"]["subcategories"] %}
                        <li>
                            <input type="checkbox" name="subcategory" value="{{ subcategory }}" onchange="updatePrompt()">
                            {{ subcategory }}
                        </li>
                    {% endfor %}
                </ul>
                <label for="number">Number of items:</label>
                <input type="number" name="number" min="1" max="100" value="1" onchange="updatePrompt()"><br><br>
            </form>
            <div class="generated-prompt">
                <span id="generated-prompt">Your prompt will appear here.</span>
                <span class="copy-icon" onclick="copyToClipboard()">📋 Copy</span>
            </div>
        </div>
    </body>
    </html>
    """, categories=categories)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
