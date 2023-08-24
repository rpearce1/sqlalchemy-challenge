# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    query_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    prcp_query = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()

    session.close()

    prcp_year = []
    for date, prcp in prcp_query:
        date_dict = {}
        date_dict[date] = prcp
        prcp_year.append(date_dict)

    return(jsonify(prcp_year))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = session.query(Station.station).all()
    station_list = [station.station for station in station_query]
    session.close()
    return(jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    query_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    session = Session(engine)
    tobs_query = session.query(Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > query_date)).all()
    session.close()
    tobs_list = [tobs.tobs for tobs in tobs_query]
    return(jsonify(tobs_list))


@app.route("/api/v1.0/<start>")
def temp_summary_start(start):
    query_date = datetime.strptime(start,'%Y-%m-%d').date()
    session = Session(engine)
    query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= query_date).all()
    session.close()
    stats = {'TMIN':query[0][0],'TMAX':query[0][1],'TAVG':query[0][2]}
    return(jsonify(stats))
    

@app.route("/api/v1.0/<start>/<end>")
def temp_summary_start_end(start,end):
    start_date = datetime.strptime(start,'%Y-%m-%d').date()
    end_date = datetime.strptime(end,'%Y-%m-%d').date()
    session = Session(engine)
    query = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter((Measurement.date >= start_date) & (Measurement.date <= end_date)).all()
    session.close()
    stats = {'TMIN':query[0][0],'TMAX':query[0][1],'TAVG':query[0][2]}
    return(jsonify(stats))


if __name__ == '__main__':
    app.run(debug=True)
