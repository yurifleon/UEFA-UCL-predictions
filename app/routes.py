from flask import render_template, jsonify
from . import db
from .models import Prediction
from flask import current_app as app
from sqlalchemy import func
import json
from flask import request, redirect, url_for, flash

@app.route("/submit_prediction", methods=["POST"])
def submit_prediction():
    if request.method == "POST":
        try:
            # Grab form data (adjust as per form field names)
            user_name = request.form["name"]
            match = request.form["match"]
            prediction = request.form["prediction"]

            # Example: Save to DB
            db.session.add(Prediction(name=user_name, match=match, prediction=prediction))
            db.session.commit()
            flash("Prediction submitted successfully!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"Error submitting prediction: {str(e)}", "danger")
            return redirect(url_for("index"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/leaderboard")
def api_leaderboard():
    results = db.session.query(
        Prediction.name,
        func.sum(Prediction.score).label("total_score")
    ).group_by(Prediction.name).order_by(func.sum(Prediction.score).desc()).all()

    return jsonify([{"name": row.name, "score": row.total_score} for row in results])

def score_prediction(predicted, actual):
    if predicted == actual:
        return 3
    p1, p2 = map(int, predicted.split('-'))
    a1, a2 = map(int, actual.split('-'))
    pred_result = (p1 > p2) - (p1 < p2)
    act_result = (a1 > a2) - (a1 < a2)
    return 1 if pred_result == act_result else 0

def load_predictions_from_json(path="predictions_vs_actual.json"):
    with open(path) as f:
        data = json.load(f)

    db.session.query(Prediction).delete()
    db.session.commit()

    actuals = data["actual"]
    users = data["users"]

    for user, preds in users.items():
        for match, prediction in preds.items():
            actual = actuals.get(match)
            score = score_prediction(prediction, actual) if actual else 0
            db.session.add(Prediction(
                name=user, match=match, prediction=prediction, actual=actual, score=score
            ))
    db.session.commit()
A

