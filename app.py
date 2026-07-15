from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Sir, Welcome to Flask Application<br>Flask Application is running successfully on localhost"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


