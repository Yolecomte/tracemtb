from flask import Flask, flash, request, render_template, redirect, url_for, Response, Blueprint
from flask import current_app as app
from werkzeug.utils import secure_filename
from traceVtt import db
from traceVtt.models import Traces
import os

from .utils import DB_GeoJson
import geojson
import gpxpy
from gpxpy import gpx as _gpx

traces = Blueprint('traces', __name__, static_folder='static')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def conn():
    return DB_GeoJson(**app.config['POSTGRES'])


@traces.route('/')
def index():
    return redirect(url_for('base.home'))

    
@traces.route('/page/')
@traces.route('/page/<int:page>')
def home(page=1):
    """
    Retrieve all the traces and paginate them
    """
    per_page = app.config['PER_PAGE']
    traces = Traces.query.order_by(Traces.created_at.desc()).paginate(page, per_page, error_out=False)
    return render_template('traces/index.html', 
                           traces=traces, 
                           home_button=False)


@traces.route('/api/traces/')
def api_traces():
    """
    Retrieve all geom traces in db to show on the map 
    """
    traces = conn().get_table_as_geojson(Traces.__tablename__)
    return geojson.dumps(traces, 
                         indent=4, 
                         sort_keys=True, 
                         default=str)


@traces.route('/new/', methods=['POST', 'GET'])
def new_trace():
    """
    Create a new trace from a user drawing
    """
    if request.method == 'POST':
        db.session.add(Traces(request.form['name'],
                              request.form['comment'],
                              request.form['type'],
                              geom='SRID=4326;'+request.form['wkt_geom']))
        db.session.commit()
        
        flash("Your trace has been successfully created, Thank's", 'success')
        return redirect(url_for('base.home'))

    return render_template('traces/new_trace.html', 
                           types_available=app.config['TRACKS_TYPES'], 
                           home_button=True)


@traces.route('/new/gpx/', methods=['POST', 'GET'])
def new_trace_gpx():
    """
    Create a new trace from a GPX file
    """
    if request.method == 'POST':
        error = 0
        if 'gpx_file' not in request.files:
            error += 1
            flash('No file supplied...', 'error')
            gpx_file = None
        else:
            gpx_file = request.files['gpx_file']
        
        if request.form['name'] in (None, '', ' ',):
            error += 1
            flash('Please give a name to your trace!', 'error')      
        try:
            if not allowed_file(gpx_file.filename):
                error += 1
                flash('Your file is not a valid GPX file', 'error')
        except Exception as _:
            pass

        if error:
            return redirect(request.url)
        gpx = None
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
                              geom=wkt))
        db.session.commit()
        flash('Your trace has been successfully loaded!', 'success')
    
        return redirect(url_for('base.home'))
    
    return render_template('traces/new_gpx_trace.html', 
                           types_available=app.config['TRACKS_TYPES'], 
                           home_button=True)


@traces.route('/delete/<trace_id>')
def delete_trace(trace_id):
    """
    Delete a trace
    """
    db.session.delete(Traces.query.get(trace_id))
    db.session.commit()
    flash('The trace has been succesfully deleted!', 'success')
    return redirect(url_for('base.home'))


@traces.route('/<trace_id>')
def trace(trace_id):
    """
    Retrieve single trace datas 
    """
    trace_data = Traces.query.get(trace_id)
    return render_template('traces/trace_detail.html',
                           trace=trace_data,
                           home_button=True)


@traces.route('/api/traces/<trace_id>')
def api_trace(trace_id):
    """
    Retrieve the geometry of a single trace to show it on the map
    """
    trace_data = conn().get_single_data_as_geojson(Traces.__tablename__, trace_id)
    return geojson.dumps(trace_data,
                         indent=4, 
                         sort_keys=True, 
                         default=str)


@traces.route('/<trace_id>/edit', methods=['GET', 'POST'])
def edit_trace(trace_id):
    """
    Edit an existing trace
    """
    if request.method == 'POST':
        db.session.query(Traces).filter(Traces.id == trace_id).update(
                                {'name': request.form['name'],
                                 'comment': request.form['comment'],
                                 'type_trace': request.form['type'],
                                 'geom': 'SRID=4326;'+request.form['wkt_geom']})
        db.session.commit()
        flash('Your trace has been succesfully updated!', 'success')
        return redirect(url_for('traces.trace', trace_id=trace_id))
    trace_data = Traces.query.get(trace_id)
    return render_template('traces/trace_edit.html',
                           trace=trace_data,
                           types_available=app.config['TRACKS_TYPES'],
                           home_button=True)


@traces.route('/api/traces/download/<trace_id>')
def download(trace_id):
    """
    Create a GPX file and expose it to the user for downloading
    """
    trace_data = conn().get_single_data_as_geojson(Traces.__tablename__, trace_id)

    gpx = _gpx.GPX()
        
    coords = list(geojson.utils.coords(trace_data[0]))

    gpx_track = _gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    
    gpx_segment = _gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for coord in coords:
        gpx_segment.points.append(_gpx.GPXTrackPoint(coord[0], coord[1], elevation=0))
    
    return Response(gpx.to_xml(),
                    mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=track.gpx"})
