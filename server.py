from flask import Flask, request, current_app

flaskapp = Flask(__name__)

def run(conn, port = 5001, debug = True):
    # runs and sets up the flask app
    flaskapp.config['connection'] = conn
    flaskapp.run(port=port, debug= debug)

@flaskapp.route('/receive', methods=["POST"])
def hello_world(self):
    body = request.form.get("text")
    conn = current_app.config['connection']
    conn.send([body])
    # import pdb;pdb.set_trace()
    return "200"



