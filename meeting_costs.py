from flask import Flask, render_template, request, jsonify
import json
import os
template_dir = os.path.dirname(__file__)
app = Flask(__name__,
template_folder = template_dir)

# Średnia pensja w KSM (dane z 2025)
average_salary = 14000  # PLN miesięcznie (brutto brutto)

# Ilość osób na spotkaniu
people_count = 0

# Skumulowany koszt spotkania
meeting_cost = 0

# Czy spotkanie jest aktywne
is_meeting_running = False

# Plik z historią spotkań
history_file = 'meeting_history.json'

# Wczytaj historię spotkań z pliku
def load_history():
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            return json.load(file)
    else:
        return []

# Zapisz historię spotkań do pliku
def save_history(history):
    with open(history_file, 'w') as file:
        json.dump(history, file)


def update_cost():
    global meeting_cost
    global people_count
    global is_meeting_running
    if is_meeting_running:
        # Oblicz koszt na sec
        second_cost = (average_salary / 160) * people_count / 3600  # 160 godzin w miesiącu
        meeting_cost += second_cost

@app.route('/')
def index():
    meeting_history = load_history()
    return render_template("cost_template.html", average_salary=average_salary, people_count=people_count, meeting_cost=round(meeting_cost, 2), meeting_history=meeting_history)


@app.route('/start_meeting', methods=['POST'])
def start_meeting():
    global is_meeting_running
    global people_count
    global meeting_title
    people_count = int(request.form['people_count'])
    meeting_title = request.form['meeting_title']
    is_meeting_running = True
    return 'Spotkanie rozpoczęte'

@app.route('/stop_meeting', methods=['POST'])
def stop_meeting():
    global is_meeting_running
    is_meeting_running = False
    return 'Spotkanie zatrzymane'

@app.route('/reset_meeting', methods=['POST'])
def reset_meeting():
    global meeting_cost
    global is_meeting_running
    global people_count
    global meeting_title
    meeting_history = load_history()
    meeting_history.append({'title': meeting_title, 'cost': round(meeting_cost, 2)})
    save_history(meeting_history)
    meeting_cost = 0
    is_meeting_running = False
    people_count = 0
    return 'Spotkanie zresetowane'

@app.route('/get_cost')
def get_cost():
    global meeting_cost
    return str(round(meeting_cost, 2))

@app.route('/get_history')
def get_history():
    return jsonify(load_history())

# Zaplanuj aktualizację kosztu co minutę
import schedule
import time
import threading

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(1).seconds.do(update_cost)

# Uruchom wątek z harmonogramem
thread = threading.Thread(target=run_schedule)
thread.daemon = True  # Zakończ wątek przy zamknięciu programu
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
