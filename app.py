from flask import Flask, request, jsonify, render_template
from starter_preprocess import TextPreprocessor

app = Flask(__name__)
tp = TextPreprocessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clean', methods=['POST'])
def clean_text():
    data = request.get_json(force=True, silent=True)
    if not data or 'url' not in data:
        return jsonify({"success": False, "error": "Missing 'url'"}), 400
    try:
        raw = tp.fetch_from_url(data['url'])
        cleaned = tp.full_clean(raw)
        stats = tp.get_text_statistics(cleaned)
        summary = tp.create_summary(cleaned, 3)
        return jsonify({
            "success": True,
            "preview": cleaned[:500],
            "statistics": stats,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    data = request.get_json(force=True, silent=True)
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Missing 'text'"}), 400
    try:
        cleaned = tp.full_clean(data['text'])
        stats = tp.get_text_statistics(cleaned)
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
