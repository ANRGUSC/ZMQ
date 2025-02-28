from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def serve_ui():
    return send_from_directory('.', 'index.html')  # Serve the HTML UI

if __name__ == '__main__':
    print("✅ UI Server running at http://0.0.0.0:8080/")
    app.run(host="0.0.0.0", port=8080, debug=True)
