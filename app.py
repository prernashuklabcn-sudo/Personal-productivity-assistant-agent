from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

JSON_FILE = 'tasks.json'

def load_data():
    if not os.path.exists(JSON_FILE):
        return {"tasks": [], "todos": []}
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_data()
    tasks = data.get("tasks", [])
    todos = data.get("todos", [])
    
    total_target = 0
    total_studied = 0
    
    for task in tasks:
        target = task.get("target_min", 1)
        studied = task.get("studied_min", 0)
        total_target += target
        total_studied += studied
        
        if target > 0:
            pct = int((studied / target) * 100)
        else:
            pct = 0
        task["percentage"] = pct

    overall_pct = int((total_studied / total_target * 100)) if total_target > 0 else 0

    # Dynamic Motivational Message based on percentage
    if overall_pct == 100:
        quote = "🎉 Outstanding! You hit 100%! Absolute perfection. Keep this unstoppable momentum going!"
    elif overall_pct >= 75:
        quote = "🔥 Brilliant work! You've crossed 75%! You are extremely close to 100%, push just a little bit more!"
    elif overall_pct > 0:
        quote = "👍 Good start! Every single minute counts. Keep it up, stay consistent, and you'll reach your goal!"
    else:
        quote = "🚀 Consistency and focused effort every single day lead to massive results. Let's start tracking!"

    return render_template('index.html', tasks=tasks, todos=todos, total_studied=total_studied, total_target=total_target, overall_pct=overall_pct, quote=quote)

@app.route('/add_task', methods=['POST'])
def add_task():
    subject = request.form.get('subject')
    target_min = int(request.form.get('target_min', 0))
    
    data = load_data()
    tasks = data.get("tasks", [])
    
    new_id = len(tasks)
    new_task = {
        "id": new_id,
        "subject": subject,
        "target_min": target_min,
        "studied_min": 0
    }
    tasks.append(new_task)
    data["tasks"] = tasks
    save_data(data)
    
    return redirect(url_for('index'))

@app.route('/log_study/<int:task_id>', methods=['POST'])
def log_study(task_id):
    studied_mins = int(request.form.get('studied_mins', 0))
    
    data = load_data()
    tasks = data.get("tasks", [])
    
    for task in tasks:
        if task.get("id") == task_id:
            task["studied_min"] = task.get("studied_min", 0) + studied_mins
            break
            
    data["tasks"] = tasks
    save_data(data)
    return redirect(url_for('index'))

@app.route('/add_todo', methods=['POST'])
def add_todo():
    todo_text = request.form.get('todo_text')
    if todo_text:
        data = load_data()
        todos = data.get("todos", [])
        todos.append(todo_text)
        data["todos"] = todos
        save_data(data)
    return redirect(url_for('index'))

@app.route('/reset_data', methods=['POST'])
def reset_data():
    save_data({"tasks": [], "todos": []})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    