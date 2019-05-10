from flask import Flask, request, render_template
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model'))
from model import runModel
app = Flask(__name__)

app.config['userDataFolder'] = '../userData/'

@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "GET":
        return render_template('index.html', results="None", msg="Please choose a jpg or png file.")
    
    elif request.method == 'POST':
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', results="results", msg="Please choose a valid file.")
        
        else:
            # remove old images in userData folder
            toRemove = [ temp for temp in os.listdir(app.config['userDataFolder'])]
            for temp in toRemove:
                os.remove(os.path.join(app.config['userDataFolder'], temp))
            
            # save new image to userData folder
            file.save(os.path.join(app.config['userDataFolder'], file.filename))

            # run model with saved weights on new user image
            result = runModel(file.filename)
            return render_template('index.html', results=result, msg="Success!")

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='0.0.0.0') 
