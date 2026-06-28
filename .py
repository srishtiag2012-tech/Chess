from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

ALL_GAMES = {}

# The entire visual app is kept inside the python code permanently
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile AI Chess Coach</title>
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; background: #1a1a1a; color: #ffffff; margin: 0; padding: 20px; }
        .session-info { color: #4caf50; font-size: 14px; margin-bottom: 20px; font-weight: bold; }
        .board-container { width: 280px; height: 280px; margin: 20px auto; background: #eeddcc; border: 4px solid #333333; display: flex; flex-wrap: wrap; }
        .square { width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; }
        .dark { background: #b58863; }
        .light { background: #f0d9b5; }
        .coach-dashboard { background: #2a2a2a; border-radius: 12px; padding: 15px; max-width: 320px; margin: 20px auto; border-left: 5px solid #4caf50; text-align: left; }
        .coach-dashboard h4 { color: #4caf50; margin: 0 0 8px 0; }
    </style>
</head>
<body>
    <h1>♟️ Chess Coach Pro</h1>
    <div class="session-info">Your Session ID: <span id="id-tag">Generating...</span></div>
    <div class="board-container" id="board-grid"></div>
    <div class="coach-dashboard">
        <h4>💡 Active Coach Guidance</h4>
        <p id="advice-text">Tap any square on the board to simulate moving a piece!</p>
    </div>
    <script>
        const uniqueUserId = "User_" + Math.floor(Math.random() * 900000 + 100000);
        document.getElementById('id-tag').innerText = uniqueUserId;

        const boardGrid = document.getElementById('board-grid');
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                const square = document.createElement('div');
                const isLight = (r + c) % 2 === 0;
                square.className = `square ${isLight ? 'light' : 'dark'}`;
                if (r === 1) square.innerText = '♟';
                if (r === 6) square.innerText = '♙';
                square.onclick = () => communicateWithPythonBackend("e2e4");
                boardGrid.appendChild(square);
            }
        }

        async function communicateWithPythonBackend(moveNotation) {
            document.getElementById('advice-text').innerText = "Connecting to live cloud server...";
            try {
                // By using a relative route, it dynamically connects safely on the internet!
                const transmissionStream = await fetch('/process-move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId: uniqueUserId, move: moveNotation })
                });
                const runtimeData = await transmissionStream.json();
                document.getElementById('advice-text').innerText = `Computer played ${runtimeData.botMove}. \\n\\nTip: ${runtimeData.coachAdvice}`;
            } catch (networkError) {
                console.error("Transmission error:", networkError);
                document.getElementById('advice-text').innerText = "⚠️ Connection Failed! Make sure your cloud server is awake.";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_INTERFACE

@app.route('/process-move', methods=['POST'])
def process_move():
    incoming_data = request.json
    user_id = incoming_data.get('userId', 'guest')
    player_move = incoming_data.get('move', '')
    
    if user_id not in ALL_GAMES:
        ALL_GAMES[user_id] = []
        
    ALL_GAMES[user_id].append(player_move)
    total_moves = len(ALL_GAMES[user_id])
    
    coach_tips = [
        "Control the center! Try to occupy squares e4, d4, e5, and d5 early.",
        "Develop your minor pieces! Bring out your Knights and Bishops before your Queen.",
        "Castle early! Protect your King and activate your Rook into the game.",
        "Think about safety! Always check what your opponent's last move threatens before you play."
    ]
    
    selected_tip = coach_tips[total_moves % len(coach_tips)]
    computer_counter_move = "e7e5"
    ALL_GAMES[user_id].append(computer_counter_move)
    
    return jsonify({
        "status": "success",
        "botMove": computer_counter_move,
        "coachAdvice": selected_tip
    })

if __name__ == '__main__':
    # Render assigns a dynamic cloud port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
