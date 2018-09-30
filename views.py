from flask import Flask, request, render_template, redirect, url_for
from models import db, Traces
from geoalchemy2.shape import to_shape

app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
@app.route('/traces/')
def home():
    traces = Traces.query.all()
    return render_template('index.html', traces=traces)


@app.route('/traces/new/', methods=['POST','GET'])
def new_trace():
    if request.method == 'POST':
        db.session.add(Traces(request.form['name'],
                              request.form['comment']))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_trace.html')

@app.route('/traces/delete/<trace_id>')
def delete_trace(trace_id):
    db.session.delete(Traces.query.get(trace_id))
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/traces/<trace_id>')
def trace(trace_id):
    trace = Traces.query.get(trace_id)
    if trace.geom is not None:
        trace.has_geom = True
        geometry = to_shape(trace.geom)
        json = geometry.asGeojson()
    else:
        trace.has_geom = False
    return render_template('trace_detail.html',trace=trace)

if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
