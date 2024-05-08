# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np  # Add the missing import
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the homepage route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last date in the database
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the last date in the database
    prev_year = dt.date.today() - dt.timedelta(days=365)

    # Query the primary station for all temperature observations from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(results))

    return jsonify(all_temps)

# Define the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

# Define the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
