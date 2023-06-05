from flask import Flask, render_template, request, redirect, flash, url_for, session
from sqlalchemy import create_engine, text

app = Flask(__name__, static_url_path="/static")

app.secret_key = '123'
engine = create_engine('sqlite:///cafes.db')
connection = engine.connect()
create_table_query = text(
    "CREATE TABLE IF NOT EXISTS userdata(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)"
)
connection.execute(create_table_query)


def getfulldata():
    result = connection.execute(text("SELECT * FROM cafe"))
    return result.all()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user_query = text("SELECT * FROM userdata WHERE username = :username")
        result = connection.execute(
            user_query, {'username': username}).fetchone()

        if result:
            stored_password = result[3]
            if password == stored_password:
                session['user'] = username
                session['logged_in'] = True
                return redirect(url_for('main'))
            else:
                flash("wrong Password")
        else:
            flash("wrong username")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_usernames = connection.execute(
            text("SELECT username FROM userdata")).fetchall()
        existing_emails = connection.execute(
            text("SELECT email FROM userdata")).fetchall()
        if (username,) in existing_usernames:
            flash("username already exists.")
        elif (email,) in existing_emails:
            flash(
                "email already exists.", "success")
        else:
            insert_query = text(
                "INSERT INTO userdata(username, email, password) VALUES (:username, :email, :password)")
            connection.execute(
                insert_query, {'username': username, 'email': email, 'password': password})
            connection.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/main')
def main():
    if 'logged_in' in session and session['logged_in']:
        dat = getfulldata()
        return render_template('main.html', data=dat, name=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        name = request.form['name']
        map_url = request.form['map_url']
        img_url = request.form['img_url']
        location = request.form['location']
        has_sockets = True if 'has_sockets' in request.form else False
        has_toilet = True if 'has_toilet' in request.form else False
        has_wifi = True if 'has_wifi' in request.form else False
        can_take_calls = True if 'can_take_calls' in request.form else False
        seats = request.form['seats']
        coffee_price = request.form['coffee_price']
        query = text('''
            INSERT INTO cafe (name, map_url, img_url, location, has_sockets, has_toilet, has_wifi, can_take_calls, seats, coffee_price)
            VALUES (:name, :map_url, :img_url, :location, :has_sockets, :has_toilet, :has_wifi, :can_take_calls, :seats, :coffee_price)
        ''')
        values = {'name': name, 'map_url': map_url, 'img_url': img_url, 'location': location, 'has_sockets': has_sockets,
                  'has_toilet': has_toilet, 'has_wifi': has_wifi, 'can_take_calls': can_take_calls, 'seats': seats, 'coffee_price': coffee_price}

        connection.execute(query, [values])
        connection.commit()
        return redirect(url_for('main'))
    return render_template('add.html')


@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    user_query = text("SELECT * FROM cafe WHERE id = :id")
    result = connection.execute(user_query, {'id': id}).fetchone()
    return render_template('update.html', row=result)


@app.route('/updatedb/<id>', methods=['GET', 'POST'])
def updatedb(id):
    if request.method == "POST":
        name = request.form['name']
        map_url = request.form['map_url']
        img_url = request.form['img_url']
        location = request.form['location']
        has_sockets = request.form.get('has_sockets') == 'true'
        has_toilet = request.form.get('has_toilet') == 'true'
        has_wifi = request.form.get('has_wifi') == 'true'
        can_take_calls = request.form.get('can_take_calls') == 'true'
        seats = request.form['seats']
        coffee_price = request.form['coffee_price']
        query = text("""
        UPDATE cafe SET name = :name, map_url = :map_url, img_url = :img_url, location = :location,
        has_sockets = :has_sockets, has_toilet = :has_toilet, has_wifi = :has_wifi,
        can_take_calls = :can_take_calls, seats = :seats, coffee_price = :coffee_price WHERE id =:id
        """)
        values = {
            'name': name, 'map_url': map_url, 'img_url': img_url, 'location': location, 'has_sockets': has_sockets, 'has_toilet': has_toilet, 'has_wifi': has_wifi, 'can_take_calls': can_take_calls, 'seats': seats, 'coffee_price': coffee_price, 'id': id
        }
        connection.execute(query, [values])
        connection.commit()
        return redirect(url_for('main'))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    connection.execute(text("DELETE FROM cafe WHERE id = {0}".format(id)))
    connection.commit()
    return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
