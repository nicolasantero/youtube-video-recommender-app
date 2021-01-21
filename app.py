import os.path
from flask import Flask, request, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import os
import json
import run_backend
import get_data #
import ml_utils #

import sqlite3 as sql  # 

import time
import youtube_dl


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


def get_predictions():

    videos = []

    with sql.connect(run_backend.db_name) as conn: # 
        c = conn.cursor() #
        for line in c.execute("SELECT * FROM videos"): #
            #(title, video_id, score, update_time)
            line_json = {"title": line[0], "video_id": line[1], "score": line[2], "update_time": line[3]} #
            videos.append(line_json)
			
    predictions = []
    for video in videos:
        predictions.append((video['video_id'], video['title'], float(video['score'])))

    predictions = sorted(predictions, key=lambda x: x[2], reverse=True)[:30]

    predictions_formatted = []
    for e in predictions:
        #print(e)
        predictions_formatted.append("<tr><th><a href=\"{link}\">{title}</a></th><th>{score}</th></tr>".format(title=e[1], link=e[0],    score=e[2]))
  
    # return '\n'.join(predictions_formatted) 
    return predictions #

# def predict_api(yt_video_id):
# #     yt_video_id = request.args.get("yt_video_id", default='')
    
#     ydl = youtube_dl.YoutubeDL({"ignoreerrors": True})
#     video_json_data = ydl.extract_info("https://www.youtube.com/watch?v={}".format(yt_video_id), download=False)

#     if video_json_data is None:
#         return "not found"

#     p = ml_utils.compute_prediction(video_json_data)
    
#     output = {"title": video_json_data['title'], "score": p}

#     return json.dumps(output)
# #     out = json.dumps(output)
    
# #     return render_template('predict.html', out = out)


class PredForm(FlaskForm):
    yt_video_id = StringField('Video id')
    submit = SubmitField('Check probability!')

# @app.route('/')
# @app.route('/home')
# def main_page():
#     preds = get_predictions() # 
#     return render_template('home.html', preds=preds)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def main_page():
    preds = get_predictions() #
    form = PredForm()
    if form.validate_on_submit():
        vid_id = form.yt_video_id.data
        return redirect(url_for('predict', vid_id=vid_id))
    return render_template('home.html', preds=preds, form=form)
    
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    out = []

#     if PredForm(request.form).validate_on_submit():
#         yt_video_pred = request.form.yt_video_id
        
    yt_video_pred = request.args.get('vid_id')
    
#     yt_video_id = request.args.get("yt_video_id", default='')
    
    ydl = youtube_dl.YoutubeDL({"ignoreerrors": True})
#     video_json_data = ydl.extract_info("https://www.youtube.com/watch?v={}".format(yt_video_id), download=False)
    video_json_data = ydl.extract_info("https://www.youtube.com/watch?v={}".format(yt_video_pred), download=False)


    if video_json_data is None:
        return "not found"

    p = ml_utils.compute_prediction(video_json_data)
    
    out.append(video_json_data['title'])
    out.append(video_json_data['webpage_url'])
    out.append(p)
#     output = {"title": video_json_data['title'], "score": p}

#     return json.dumps(output)
#     out = json.dumps(output)
    
    return render_template('predict.html', out=out)

# @app.route("/predict", methods=['GET', 'POST'])
# def predict():
#     yt_video_id = PredFrom()
#     if form.validate_on_submit():
#         flash(f'Account created for {form.username.data}!', 'success')
#         return redirect(url_for('home'))
#     return render_template('register.html', title='Register', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')