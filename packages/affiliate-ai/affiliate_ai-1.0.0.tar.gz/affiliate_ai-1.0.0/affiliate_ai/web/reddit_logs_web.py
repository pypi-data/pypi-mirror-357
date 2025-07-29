from flask import Flask, render_template, request, redirect
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
LOG_FILE = Path("affiliate_ai/logs/reddit_publications.json")

@app.route("/reddit-logs", methods=["GET"])
def reddit_logs():
    if not LOG_FILE.exists():
        return "Aucun log Reddit trouvé."
    data = json.loads(LOG_FILE.read_text())
    logs = sorted(data, key=lambda x: x['timestamp'], reverse=True)
    return render_template("reddit_logs.html", logs=logs)

@app.route("/republish/<int:index>", methods=["POST"])
def republish(index):
    data = json.loads(LOG_FILE.read_text())
    if index >= len(data):
        return "❌ Log introuvable."

    log = data[index]
    subreddit = request.form["new_subreddit"]
    title = request.form.get("new_title") or log["title"]

    # Simuler reposte dans les logs (dans un cas réel : appel publisher.py)
    new_log = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "subreddit": subreddit,
        "url": "https://reddit.com/r/" + subreddit + "/repost"  # mock
    }
    data.append(new_log)
    LOG_FILE.write_text(json.dumps(data, indent=2))
    return redirect("/reddit-logs")

@app.route("/delete-log/<int:index>", methods=["POST"])
def delete_log(index):
    data = json.loads(LOG_FILE.read_text())
    if 0 <= index < len(data):
        del data[index]
        LOG_FILE.write_text(json.dumps(data, indent=2))
    return redirect("/reddit-logs")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
