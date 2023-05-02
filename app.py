# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
from sqlalchemy import MetaData
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Save references to each table
Measurement = Base.classes.measurement
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
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/end <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()

    # Convert the query results to a dictionary
    precip_dict = {}
    for date, prcp in results:
        precip_dict[date] = prcp

    # Close the session
    session.close()

    # Return the JSON representation of the dictionary
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station[0] for station in results]

    # Close the session
    session.close()

    # Return the JSON representation of the list
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # First, get the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label('count')) \
                         .group_by(Measurement.station) \
                         .order_by(func.count(Measurement.station).desc()) \
                         .first()

    # Then, query the dates and temperature observations of the most-active station for the previous year of data.
    results = session.query(Measurement.date, Measurement.tobs) \
                  .filter(Measurement.station == most_active_station.station) \
                  .filter(Measurement.date >= one_year_ago_date) \
                  .all()

    # convert query results to a dictionary
    tobs_dict = {}
    for date, tobs in results:
        tobs_dict[date] = tobs

    # Close the session
    session.close()

    # Return the JSON representation of the dictionary
    return jsonify(tobs_dict)

# Define a Flask API route for the start date
@app.route("/api/v1.0/<start>")
def start_date(start):

    start = dt.datetime.strptime(start, '%Y-%m-%d') - dt.timedelta(days=235)
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                     .filter(Measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temps = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    # Close the session
    session.close()

    # Return the JSON representation of the list
    return jsonify(temps)

# Define a Flask API route for the start-end range
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    start = dt.datetime.strptime(start, '%Y-%m-%d') - dt.timedelta(days=235)
    end = dt.datetime.strptime(start, '%Y-%m-%d') - dt.timedelta(days=500)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for all dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                     .filter(Measurement.date >= start) \
                     .filter(Measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temps = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    # Close the session
    session.close()

    # Return the JSON representation of the list
    return jsonify(temps)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
