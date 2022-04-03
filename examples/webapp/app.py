from flask import Flask, render_template


app = Flask(__name__)
app.config["SECRET_KEY"] = "jfoholqsdjlfoiqsdjfmlskd!kfjmiqsdfjgldif"

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/", methods=["GET"])
@app.route("/index/", methods=["GET"])
def home():
    return render_template("index.html")
