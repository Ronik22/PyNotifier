from flask import Flask, request
from flask import render_template
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from plyer import notification 
from twilio.rest import Client 
import time 

from apscheduler.schedulers.background import BackgroundScheduler
import atexit

##############  ENTER CREDENTIALS HERE TO RECEIVE SMS  ##############

# Create a Twilio account if you want to send notifications of events via SMS...Ignore if you want to stick to only desktop notifications instead 

account_sid = ''      # Enter your 'ACCOUNT SID' inside the quotes
auth_token = ''       # Enter your 'AUTH TOKEN' inside the quotes
twilio_from_num = ''    # Enter your twilio phone no. inside the quotes
twilio_to_num = ''      # Enter your registered twilio phone no. to which you want to send the SMS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    content = db.Column(db.Text)
    opt = db.Column(db.String(50))
    done = db.Column(db.Boolean, default=False)

    def __init__(self, content, date, time, opt):
        self.content = content
        self.date = date
        self.time = time
        self.opt = opt
        self.done = False


def notify():
    today = datetime.now()
    datenow = today.strftime("%d/%m/%Y")
    timenow = today.strftime("%I:%M %p")
    tasks = Task.query.all()
    for task in tasks:
        if task.date == datenow and task.time == timenow:
            if task.opt == 'sms':
                notify_via_Sms(task.content)
                delete_task(task.id)
                return redirect('/')
            else:
                notify_via_Notification(task.content)
                delete_task(task.id)
                return redirect('/')


def notify_via_Notification(content):
    notification.notify( 
                    title="Reminder...", 
                    message=content,
                    app_name="PyNotifier by Ronik", 
                    timeout=10
                )

def notify_via_Sms(content):
    client = Client(account_sid, auth_token) 
    message = client.messages.create( 
                                    from_=twilio_from_num, 
                                    body =content, 
                                    to =twilio_to_num
                                    ) 

scheduler = BackgroundScheduler()
scheduler.add_job(func=notify, trigger="interval", seconds=5)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def tasks_list():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/task', methods=['POST'])
def add_task():
    content = request.form['content']
    date = request.form['date']
    time = request.form['time']
    opt = request.form['opt']
    if not content or not date or not time or not opt:
        return 'Incomplete Details'

    task = Task(content, date, time, opt)
    db.session.add(task)
    db.session.commit()
    return redirect('/')

@app.route('/edit/<task_id>', methods=['GET','POST'])
def edit(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        task.date = request.form['date']
        task.time = request.form['time']
        task.content = request.form['content']
        task.opt = request.form['opt']
        db.session.commit()     
        return redirect('/')
    else:
        return render_template('edit.html',task=task)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/')

    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return redirect('/')
    if task.done:
        task.done = False
    else:
        task.done = True

    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
