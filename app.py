from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
app = Flask(__name__)

DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"

BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
   return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
  if request.method == 'GET':  
    
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone();
    
    return render_template("buggy-form.html", buggy = record)
  elif request.method == 'POST':
    msg=""
    qty_wheels = request.form['qty_wheels']
    flag_color = request.form['flag_color']
    flag_color_secondary = request.form['flag_color_secondary']
    flag_pattern = request.form['flag_pattern']
    power_type = request.form['power_type']
    hamster_booster = request.form['hamster_booster']
    if not qty_wheels.isdigit():
       msg = f"Sorry, you didn't enter the number of wheels correctly: {qty_wheels}, please use an integer value"
       return render_template("buggy-form.html", msg = msg)
    if not (int(qty_wheels) % 2) == 0:
       msg = ("The number of wheels needs to be even")
       return render_template("buggy-form.html", msg = msg)
    colourlist = ["black", "white", "grey", "red", "purple", "green", "yellow", "navy", "blue", "orange", "gold", "silver", "brown", "maroon"]
    if flag_color not in colourlist:
       msg = f"Sorry, you didn't enter a recognised colour: {flag_color}"
       return render_template("buggy-form.html", msg = msg)
    if flag_color_secondary == flag_color:
       msg = f"Sorry, your secondary flag colour must not be the same as the main flag colour: {flag_color}"
       return render_template("buggy-form.html", msg = msg)
    if flag_color_secondary not in colourlist:
       msg = f"Sorry, you didn't enter a recognised colour: {flag_color_secondary}, please try again."
       return render_template("buggy-form.html", msg = msg)
    if not hamster_booster.isdigit():
       msg = f"Sorry power type must be hamster to use hamster boosters"
       return render_template("buggy-form.html", msg = msg)
    if not hamster_booster.isdigit():
        msg = f"Sorry, you didn't enter the number of hamster booster correctly, please use an integer: {hamster_booster}"
        return render_template("buggy-form.html", msg = msg)
    powertypelist = ["petrol", "fusion", "steam", "bio", "electric", "rocket", "hamster", "thermo", "solar", "wind"]
    msg = f"flag_color={flag_color}" , f"flag_color_secondary={flag_color_secondary}" , f"flag_pattern={flag_pattern}" , f"power_type={power_type}", f"hamster_booster={hamster_booster}"
    try:
         with sql.connect(DATABASE_FILE) as con:
           cur = con.cursor()
           cur.execute("UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, hamster_booster=? WHERE id=?",
           (qty_wheels, flag_color, flag_color_secondary, flag_pattern, power_type, hamster_booster, DEFAULT_BUGGY_ID)
            )
           con.commit()
           msg = "Record successfully saved"
    except:
       con.rollback()
       msg = "error in update operation"
    finally:
       con.close()
    return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies")
  record = cur.fetchone(); 
  return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/new')
def edit_buggy():
  return render_template("buggy-form.html")


#------------------------------------------------------------
# get JSON from current record
#   this is still probably right, but we won't be
#   using it because we'll be dipping diectly into the
#   database
#------------------------------------------------------------
@app.route('/json')
def summary():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
  return jsonify(
      {k: v for k, v in dict(zip(
        [column[0] for column in cur.description], cur.fetchone())).items()
        if (v != "" and v is not None)
      }
    )

#------------------------------------------------------------
# delete the buggy
#   don't want DELETE here, because we're anticipating
#   there always being a record to update (because the
#   student needs to change that!)
#------------------------------------------------------------
@app.route('/delete', methods = ['POST'])
def delete_buggy():
  try:
    msg = "deleting buggy"
    with sql.connect(DATABASE_FILE) as con:
      cur = con.cursor()
      cur.execute("DELETE FROM buggies")
      con.commit()
      msg = "Buggy deleted"
  except:
    con.rollback()
    msg = "error in delete operation"
  finally:
    con.close()
    return render_template("updated.html", msg = msg)


if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0")
