
import dotenv
dotenv.load_dotenv() 

import urllib, os,sys,requests, json, string, sqlite3, random, base64
import pdb, pprint
from flask import Flask, Response, redirect, url_for, render_template, flash, g, request, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bootstrap import Bootstrap
from urllib.parse import urlparse  # Python 3
from string import ascii_lowercase
from string import ascii_uppercase

app = Flask(__name__)

app.secret_key       = os.environ['KEY']
single_user_name     = os.environ['USERNAME']
single_user_password = os.environ['PASSWORD']
db_file              = os.environ['DB']

pos_chars = 'abcdefghijknpqrstuvwxyz23456789'


Bootstrap(app) # bootstrap framework support

app.config['BOOTSTRAP_SERVE_LOCAL'] = True # tell bootstrap NOT to fetch from CDNs

# login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# database setup

# for debugging
pp = pprint.PrettyPrinter(stream=sys.stderr)



# ----

def table_check():
    if not os.path.isfile(db_file):
        sys.stderr.write('Creating Table')
        create_table = """
         CREATE TABLE urls( 
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            URL TEXT NOT NULL,
            SHORT TEXT NOT NULL
            );
            """
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)
    else:
        sys.stderr.write('db exists\n')


# ----

class User(UserMixin):
    # define table entry in db for logged-in user
    def __init__(self,id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__self():
        return "%d/%s/%s" % (self.id, self.name, self.password)
        
        
@login_manager.user_loader
def load_user(id):
    # required by flask_login
    return User.query.get(int(id))




# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if (request.form['username'] == single_user_name and request.form['password'] == single_user_password):        
            id = request.form['username']
            user = User(id)
            login_user(user)
            return redirect('/')
        else:
            return abort(401)
    else:
        flash('Please Log in')
        global g
        g.single_user_name = single_user_name
        return render_template('login.html')

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    flash('login failed','error')
    flash('Please Log in','info')
    return render_template('login.html')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/',methods=["GET","POST"])
@login_required
def index():
    global g
    if request.method == "GET":
        # render enter url page
        flash('You are logged in','success')
        g.show_input_form = True
        return render_template('index.html')

    if request.method == "POST":
        # create short url, store it, and render result page
        original_url = request.form['url_to_shorten']
        if (original_url == ''):
            flash('enter a url to shorten')
            g.show_input_form = True
            return render_template('index.html')
        url = original_url

        lu_er,lu_res = lookup_by_long_url(url)
        if (lu_er):
            flash(lu_res)
            g.show_input_form = True
            return render_template('index.html')
        if (lu_res != None):
            flash('Short URL already created')
            g.show_input_form = False
            g.show_results = True
            g.short_url = request.base_url + lu_res
            g.orig_url = original_url
            return render_template('index.html')


        ran_str = ''.join(random.choice(pos_chars) for _ in range (3))
        lu_er,lu_res = lookup_by_short_url(ran_str)
        if (lu_er):
            flash('try again')
            g.show_input_form = True
            return render_template('index.html')

        with sqlite3.connect(db_file) as dbc:
            cursor = dbc.cursor()
            try:
                res = dbc.execute(
                        'INSERT INTO urls(URL,SHORT) VALUES (?,?)',
                        [url, ran_str]
                        )
            except Exception as e:
                flash('insert error:' + e.args[0])

        g.show_input_form = False
        g.show_results = True
        g.short_url = request.base_url + ran_str
        g.orig_url = original_url
        return render_template('index.html')


def lookup_by_short_url(short_url):
    with sqlite3.connect(db_file) as dbc:
        result = None
        cursor = dbc.cursor()
        try:
            res = cursor.execute('SELECT * FROM urls WHERE SHORT=?', [short_url])
            matched_record = res.fetchone()
            if matched_record is not None:
                result = matched_record
        except Exception as e:
            result = 'fetch error:' + e.args[0]
            return(True,result) # fail

        return(False,result) # success

def lookup_by_long_url(long_url):
    with sqlite3.connect(db_file) as dbc:
        result = None
        cursor = dbc.cursor()
        try:
            res = cursor.execute('SELECT * FROM urls WHERE URL=?', [long_url])
            matched_record = res.fetchone()
            if matched_record is not None:
                result = matched_record[2]
        except Exception as e:
            result = 'fetch error:' + e.args[0] + ' ' + long_url
            return(True,result)
        return(False,result)


@app.route('/<short_url_code>')
def redirect_short_url(short_url_code):
    global g
    if short_url_code == 'None':
        abort(404)
    lu_er,lu_res = lookup_by_short_url(short_url_code)
    if lu_er:
        flash(lu_res)
        return render_template('index.html')
    else:
        if (lu_res == None):
            flash("Error: Code: " + short_url_code + " not found")
            return render_template('index.html')

        (idx,long_url,short_url_code) = lu_res
        flash("Here's your url")
        g.show_input_form = False
        g.show_results    = True
        g.short_url       = request.base_url
        g.orig_url        = long_url
        return redirect(long_url)
        #return render_template('index.html')


def create_app(h,p,d):
    # start up flask web server
    table_check()
    app.run(host=h, port=p, debug=d)

################################################################################
# Execution starts here
if __name__ == '__main__':
    create_app()


