from flask import Flask, flash, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, Traces

import os

from utils import DB_GeoJson
import geojson
import gpxpy


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


app = Flask(__name__)
app.config.from_object('config')
conn = DB_GeoJson(**app.config['POSTGRES'])

@app.route('/')
def index():
    return redirect(url_for('home'))
    
@app.route('/traces/page/')
@app.route('/traces/page/<int:page>')
def home(page=1):
    per_page = 5
    traces = Traces.query.paginate(page, per_page, error_out=False)
    return render_template('index.html', traces=traces, home_button=False)

@app.route('/api/traces/')
def api_traces():
    traces = conn.get_table_as_geojson(Traces.__tablename__)
    return geojson.dumps(traces, indent=4, sort_keys=True, default=str)

@app.route('/traces/new/', methods=['POST','GET'])
def new_trace():
    if request.method == 'POST':
        db.session.add(Traces(request.form['name'],
                              request.form['comment'],
                              request.form['type'],
                              geom = 'SRID=4326;'+request.form['wkt_geom']))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_trace.html', types_available=app.config['TRACKS_TYPES'], home_button=True)

@app.route('/traces/new/gpx/', methods=['POST','GET'])
def new_trace_gpx():
    if request.method == 'POST':
        print request.files
        if 'gpx_file' not in request.files:
            flash('No file supplied...')
            return redirect(request.url)
        gpx_file = request.files['gpx_file']
        if gpx_file and allowed_file(gpx_file.filename):
            filename = secure_filename(gpx_file.filename)
            gpx_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            loaded_gpx = open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            gpx = gpxpy.parse(loaded_gpx)
        routes = gpx.routes
        tracks = gpx.tracks
        wkt = 'SRID=4326;LINESTRING('
        if routes:
            for route in routes:
                for point in route.points:
                    lat = float(point.latitude)
                    if lat > 40.0:
                        wkt = wkt + "{0} {1},".format(str(point.longitude), str(point.latitude))
            wkt = wkt[:-1] + ')'
        elif tracks:
            for track in tracks:
                for segment in track.segments:
                    for point in segment.points:
                        lat = float(point.latitude)
                        if lat > 40.0:
                            wkt = wkt + "{0} {1},".format(str(point.longitude), str(point.latitude))
            wkt = wkt[:-1] + ')'
        db.session.add(Traces(request.form['name'],
                            request.form['comment'],
                            request.form['type'],
                            geom = wkt))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_gpx_trace.html', types_available=app.config['TRACKS_TYPES'],home_button=True)        

@app.route('/traces/delete/<trace_id>')
def delete_trace(trace_id):
    db.session.delete(Traces.query.get(trace_id))
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/traces/<trace_id>')
def trace(trace_id):
    trace = Traces.query.get(trace_id)
    return render_template('trace_detail.html',trace=trace, home_button=True)

@app.route('/api/traces/<trace_id>')
def api_trace(trace_id):
    trace = conn.get_single_data_as_geojson(Traces.__tablename__, trace_id)
    return geojson.dumps(trace,indent=4, sort_keys=True, default=str)



if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
