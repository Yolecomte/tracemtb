from flask import Flask, flash, request, render_template, redirect, url_for, Response
from werkzeug.utils import secure_filename
from models import db, Traces

import os

from utils import DB_GeoJson
import geojson
import gpxpy
from gpxpy import gpx as _gpx


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
    """
    Retrieve all the traces and paginate them
    """
    per_page = app.config['PER_PAGE']
    traces = Traces.query.order_by(Traces.created_at.desc()).paginate(page, per_page, error_out=False)
    return render_template('index.html', 
                           traces=traces, 
                           home_button=False)


@app.route('/api/traces/')
def api_traces():
    """
    Retrieve all geom traces in db to show on the map 
    """
    traces = conn.get_table_as_geojson(Traces.__tablename__)
    return geojson.dumps(traces, 
                         indent=4, 
                         sort_keys=True, 
                         default=str)


@app.route('/traces/new/', methods=['POST','GET'])
def new_trace():
    """
    Create a new trace from a user drawing
    """
    if request.method == 'POST':
        db.session.add(Traces(request.form['name'],
                              request.form['comment'],
                              request.form['type'],
                              geom = 'SRID=4326;'+request.form['wkt_geom']))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_trace.html', 
                           types_available=app.config['TRACKS_TYPES'], 
                           home_button=True)

@app.route('/traces/new/gpx/', methods=['POST','GET'])
def new_trace_gpx():
    """
    Create a new trace from a GPX file
    """
    if request.method == 'POST':
        
        if 'gpx_file' not in request.files:
            flash('No file supplied...', 'error')
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
    
    return render_template('new_gpx_trace.html', 
                           types_available=app.config['TRACKS_TYPES'], 
                           home_button=True)


@app.route('/traces/delete/<trace_id>')
def delete_trace(trace_id):
    """
    Delete a trace
    """
    db.session.delete(Traces.query.get(trace_id))
    db.session.commit()
    flash('The trace has been succesfully deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/traces/<trace_id>')
def trace(trace_id):
    """
    Retrieve single trace datas 
    """
    trace = Traces.query.get(trace_id)
    return render_template('trace_detail.html',
                           trace=trace, 
                           home_button=True)


@app.route('/api/traces/<trace_id>')
def api_trace(trace_id):
    """
    Retrieve the geometry of a single trace to show it on the map
    """
    trace = conn.get_single_data_as_geojson(Traces.__tablename__, trace_id)
    return geojson.dumps(trace,
                         indent=4, 
                         sort_keys=True, 
                         default=str)


@app.route('/traces/<trace_id>/edit', methods=['GET', 'POST'])
def edit_trace(trace_id):
    """
    Edit an existing trace
    """
    if request.method == 'POST':
        db.session.query(Traces).filter(Traces.id == trace_id).update(
                                {'name' : request.form['name'],
                                 'comment': request.form['comment'],
                                 'type' : request.form['type'],
                                 'geom' : 'SRID=4326;'+request.form['wkt_geom']})
        db.session.commit()
        return redirect(url_for('trace', trace_id=trace_id))
    trace = Traces.query.get(trace_id) 
    return render_template('trace_edit.html',
                            trace=trace, 
                            types_available=app.config['TRACKS_TYPES'], 
                            home_button=True)


@app.route('/api/traces/download/<trace_id>')
def download(trace_id):
    """
    Create a GPX file and expose it to the user for downloading
    """
    trace = conn.get_single_data_as_geojson(Traces.__tablename__, trace_id)

    gpx = _gpx.GPX()
        
    coords = list(geojson.utils.coords(trace[0]))

    gpx_track = _gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    
    gpx_segment = _gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for coord in coords:
        print coord[0]
        gpx_segment.points.append(_gpx.GPXTrackPoint(coord[0], coord[1], elevation=0))
    
    return Response(gpx.to_xml(), mimetype="text/plain", headers={"Content-Disposition":"attachment;filename=track.gpx"})
	

if __name__ == '__main__':
    
    db.init_app(app)
    app.run(debug=True)
