import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
       f"Available Routes:<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start<br/>"
       f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query dates and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)
    
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    results = session.query(Station.name).all()

    session.close()
    
    #Convert list of tuples into normal list
    
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for dates and temperature observations from a year from the last data point
    Last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= Last_12_months).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()

    session.close()

    obser = list(np.ravel(results))

    return jsonify(obser)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def start_date(start=None,end=None):
    
    session = Session(engine)

    if not end:
        temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        temp1 =list(np.ravel(temp))

        return jsonify(temp1) 

    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    temp2 =list(np.ravel(temps))
    return jsonify(temp2)


if __name__ == '__main__':
    app.run(debug=True)