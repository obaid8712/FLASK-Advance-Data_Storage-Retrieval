# 1. import Flask
from flask import Flask
from flask import Flask, jsonify
import numpy as np
import pandas as pd

import datetime as dt
from dateutil.parser import parse

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
###########################################
# Connect Database and Create session
############################################
#Create engin to connect hawaii.sqlite DataBase
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
###########################################
# Write Query to access precipitation data from Database
############################################
# Calculate the date 1 year ago from the last data point in the database
max_date = session.query(Measurement.id, Measurement.station, func.max(Measurement.date), Measurement.prcp,\
                         Measurement.tobs ).all()
max_date[0][2]
max_dt=parse(max_date[0][2])
date_yago=max_dt-dt.timedelta(days=366)
# Create a dictionary from the row data and append to a list of precipitation
results_12_months = session.query(  Measurement.date, \
    func.sum(Measurement.prcp)).\
    filter(Measurement.date > date_yago).filter(Measurement.prcp != None).\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()

all_precipitation = []
for date, prcp in results_12_months:
    prcp_dict = {}    
    prcp_dict["date"] = date
    prcp_dict["prcp"] = prcp
    all_precipitation.append(prcp_dict)
###########################################
# Write Query to access List of station from Database
############################################
sta_list=session.query(Measurement.station,Station.name)\
.filter(Measurement.station == Station.station)\
.group_by(Station.station)\
.order_by(func.count(Measurement.date).desc()).all()

all_station = []
for station, name in sta_list:
    sta_dict = {}    
    sta_dict["station_id"] = station
    sta_dict["station_name"] = name
    
    all_station.append(sta_dict)
###########################################
# Write Query to access Temperature obs from Database
############################################    
# Choose the station with the highest number of temperature observations.

top_sta=sta_list[0][0]

tobs_list = session.query( Measurement.station,Measurement.tobs).\
    filter(Measurement.date > date_yago).filter(Measurement.tobs != None).\
    filter(Measurement.station == top_sta).\
    order_by(Measurement.date.desc()).all()

all_tobs = []
for station, tobs in tobs_list:
    tobs_dict = {}    
    tobs_dict["station_id"] = station
    tobs_dict["tobs"] = tobs
    
    all_tobs.append(tobs_dict)

###########################################
# CREATE MAIN FLASK APP
############################################    
# 2. Create an app, being sure to pass __name__
app_climate = Flask(__name__)

# 3. Define what to do when a user hits the index route
@app_climate.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Weather Advisory App (Hawaii... trip)!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/Tobs<br/>"
        f"/api/v1.0/< start ><br/>"
        f"/api/v1.0/< start >/< end ><br/>"       
    )

# 4. Define what to do when a user hits the /api/v1.0/precipitation route
@app_climate.route("/api/v1.0/precipitation")
def precp():
    """Return the precipitation data as json"""
   
    return jsonify(all_precipitation)

# 5. Define what to do when a user hits the /api/v1.0/stations route    
@app_climate.route("/api/v1.0/stations")
def station_list():
    """Return the station data as json"""
   
    return jsonify(all_station)

# 6. Define what to do when a user hits the /api/v1.0/Tobs route    
@app_climate.route("/api/v1.0/Tobs")
def tempobs_list():
    """Return the tobs data as json"""
   
    return jsonify(all_tobs)

# 7. Define what to do when a user hits the /api/v1.0/<start> route  
@app_climate.route("/api/v1.0/<start>")
def start_list(start):
    """Return the start date to max date data min,avg,max as json"""
    # Create new session (link) from Python to the DB
    session = Session(engine)   

    start_dt=func.strftime("%m-%d", start)

    data_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(func.strftime("%m-%d",Measurement.date) >= start_dt).\
             all()

    data_temp_list = []
    
    for min1,avg1,max1 in data_temp:
        temp_dict = {}
        temp_dict["minimum"] = min1
        temp_dict["average"] = avg1
        temp_dict["maximum"] = max1
        data_temp_list.append(temp_dict)
        
    return jsonify(data_temp_list)

# 8. Define what to do when a user hits the /api/v1.0/<start>/<end> route 
@app_climate.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return the start date to end date data min,avg,max as json"""
    # Create new session (link) from Python to the DB
    session = Session(engine)   

    start_dt2=func.strftime("%m-%d", start)
    end_dt2=func.strftime("%m-%d", end)

    data_temp2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(func.strftime("%m-%d",Measurement.date) >= start_dt2).\
            filter(func.strftime("%m-%d",Measurement.date) >= end_dt2).\
            all()

    data_temp_list2 = []
    
    for min2,avg2,max2 in data_temp2:
        temp_dict2 = {}
        temp_dict2["minimum"] = min2
        temp_dict2["average"] = avg2
        temp_dict2["maximum"] = max2
        data_temp_list2.append(temp_dict2)
        
    return jsonify(data_temp_list2)


if __name__ == "__main__":
    app_climate.run(debug=True)
