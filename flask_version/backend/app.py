from flask import Flask
from flask_cors import CORS

from routes.task_routes import task_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(task_routes, url_prefix="/api")

@app.route("/")
def home():
    return {"message": "TaskWise backend running"}

if __name__ == "__main__":
    app.run(debug=True)