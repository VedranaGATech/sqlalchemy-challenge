# import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

######################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# find the last date in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Calculate the date 1 year ago from the last data point in the database
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

# Create an app
app = Flask(__name__)


# Flask Routes
# Define what to do when user hits the index route
@app.route("/")
def home():
    return (
        f"Welcome to Hawaii Climate App<br/> "
        f"List of available routes:<br/>"
        f"<br/>"         
        f"The list of precipitation data with dates:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<br/>"
        f"The list of stations from the dataset:<br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<br/>"
        f"The list of temperature observations of the most-active station for the previous year of data:<br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<br/>"
        f"Min, Max. and Avg. temperatures for given start date: (enter desired 'yyyy-mm-dd' for start date)<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. Max. and Avg. temperatures for given start and end date: (enter desired 'yyyy-mm-dd' for start and date):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"example <a href='/api/v1.0/min_max_avg/2017-01-01/2017-03-23'>/api/v1.0/min_max_avg/2017-01-01/2017-03-23</a>"
    )

# create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session link
    session = Session(engine)

    # Query prcp and date values 
    results = session.query(Measurement.date, Measurement.prcp).all()
        
    session.close()
    
    # Create a dictionary with date and prcp 
    precipitation = []
    for result in results:
        r = {}
        r[result[0]] = result[1]
        precipitation.append(r)

    return jsonify(precipitation)


# create stations route    
@app.route("/api/v1.0/stations")
def stations():
    # Create session link
    session = Session(engine)
    
    # Query to get stations list
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert list for each station and name
    station_list = []
    for result in results:
        r = {}
        r["station"]= result[0]
        r["name"] = result[1]
        station_list.append(r)
    
    # jsonify the list
    return jsonify(station_list)


# create temperatures route
@app.route("/api/v1.0/tobs")
def tobs():
    # create session link
    session = Session(engine)
    
    #query_date is "2016-08-23" for the last year query
    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= query_date).all()

    session.close()

    # show date and temperature values
    tobs_list = []
    for result in results:
        r = {}
        r["date"] = result[1]
        r["temperature"] = result[0]
        tobs_list.append(r)

    # jsonify the list
    return jsonify(tobs_list)


# create start route
@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    # create session link
    session = Session(engine)

       #convert date to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    st_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        st_list.append(r)

    # jsonify the result
    return jsonify(st_list)

# create start and end route
@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    #convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start and end date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    start_end_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        start_end_list.append(r)

    # jsonify the result
    return jsonify(start_end_list)

#run the app
if __name__ == "__main__":
    app.run(debug=True)