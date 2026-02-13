from flask import Flask

# Create a Flask app instance
app = Flask(__name__)

# Define your first {called a "route"}
@app.route('/')
def home():
    return "Hello, Harsh! Welcome to Flask "

# Run the app 
if __name__ == '__main__':
    app.run(debug=True)

    