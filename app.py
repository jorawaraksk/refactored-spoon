import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Merged VJ Save & Compressor Bot is running smoothly."

if __name__ == "__main__":
    # Dynamically bind to the port provided by the host environment
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
