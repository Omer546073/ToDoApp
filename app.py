from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    completed = db.Column(db.Boolean, nullable=False, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        priority = request.form.get('priority', 'Medium')
        todo = Todo(title=title, desc=desc, priority=priority)
        db.session.add(todo)
        db.session.commit()
        return redirect("/")

    # Optional filter: /?filter=active or /?filter=completed
    status = request.args.get('filter', 'all')
    query = Todo.query
    if status == 'active':
        query = query.filter_by(completed=False)
    elif status == 'completed':
        query = query.filter_by(completed=True)

    allTodo = query.order_by(Todo.date_created.desc()).all()
    return render_template('index.html', allTodo=allTodo, status=status)

@app.route('/complete/<int:sno>')
def complete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        todo.completed = not todo.completed
        db.session.commit()
    return redirect("/")

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo is None:
        return redirect("/")

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        todo.priority = request.form.get('priority', todo.priority)
        db.session.commit()
        return redirect("/")

    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect("/")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stats')
def stats():
    total = Todo.query.count()
    completed = Todo.query.filter_by(completed=True).count()
    active = total - completed
    high = Todo.query.filter_by(priority="High").count()
    medium = Todo.query.filter_by(priority="Medium").count()
    low = Todo.query.filter_by(priority="Low").count()
    return render_template(
        'stats.html',
        total=total, completed=completed, active=active,
        high=high, medium=medium, low=low
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
