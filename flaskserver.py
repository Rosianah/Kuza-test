from flask import Flask, request
import subprocess

flaskapp = Flask(__name__)

class server:
        
    @flaskapp.route('/receive', methods=["POST"])
    def hello_world(self):
        body = request.form.get("text")
        print(body)
        return "200"

    flaskapp.run(port=5001, debug=True)



