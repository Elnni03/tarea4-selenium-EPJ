from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = 'crud-tareas-secret-key'

DB_FILE = 'tasks.json'

# ── Helpers ──────────────────────────────────────────────────────────────────
def load_tasks():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_next_id(tasks):
    return max((t['id'] for t in tasks), default=0) + 1

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    tasks = load_tasks()
    status_filter = request.args.get('status', 'all')
    if status_filter == 'pending':
        tasks = [t for t in tasks if not t['completed']]
    elif status_filter == 'completed':
        tasks = [t for t in tasks if t['completed']]
    return render_template('index.html', tasks=tasks, filter=status_filter)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', 'media')

        if not title:
            flash('El título es obligatorio.', 'error')
            return render_template('create.html')

        # Validate date format
        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha inválido. Use YYYY-MM-DD.', 'error')
                return render_template('create.html')

        tasks = load_tasks()
        new_task = {
            'id': get_next_id(tasks),
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tasks.append(new_task)
        save_tasks(tasks)
        flash('Tarea creada exitosamente.', 'success')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', 'media')

        if not title:
            flash('El título es obligatorio.', 'error')
            return render_template('edit.html', task=task)

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha inválido.', 'error')
                return render_template('edit.html', task=task)

        task['title'] = title
        task['description'] = description
        task['due_date'] = due_date
        task['priority'] = priority
        save_tasks(tasks)
        flash('Tarea actualizada correctamente.', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', task=task)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    flash('Tarea eliminada.', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        task['completed'] = not task['completed']
        save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    pending = total - completed
    by_priority = {
        'alta': sum(1 for t in tasks if t['priority'] == 'alta'),
        'media': sum(1 for t in tasks if t['priority'] == 'media'),
        'baja': sum(1 for t in tasks if t['priority'] == 'baja'),
    }
    return render_template('dashboard.html', total=total,
                           completed=completed, pending=pending,
                           by_priority=by_priority, tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
