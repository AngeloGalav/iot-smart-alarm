import React, { useState, useEffect } from "react";
import Alarm from "./Alarm";
import api from "../api";
import "./Hero.css"

const Hero = () => {
  const [alarms, setAlarms] = useState([]);

  // fetch alarms from the backend on mount
  useEffect(() => {
    fetchAlarms();
  }, []);

  // fetches alarms all alarms
  const fetchAlarms = async () => {
    try {
      const data = await api.getAlarms();
      setAlarms(data); // update local state
    } catch (error) {
      console.error("Error fetching alarms:", error);
    }
  };

  const addAlarm = async () => {
    try {
      // default alarm properties
      const newAlarm = {
        time: "08:00",
        days: [], // default to no weekdays selected
        active: true,
      };

      const data = await api.createAlarm(newAlarm);
      setAlarms([...alarms, data.alarm]); // update local state
    } catch (error) {
      console.error("Error adding alarm:", error);
    }
  };

  const deleteAlarm = async (id) => {
    try {
      await api.deleteAlarm(id);
      setAlarms(alarms.filter((alarm) => alarm.id !== id)); // update local state
    } catch (error) {
      console.error(`Error deleting alarm for id ${id} : ${error}`);
    }
  };

  return (
    <div className="flex-grow container mx-auto p-4">
      <nav className="my-navbar m-1">
      <div>
      <h1 className="text-3xl font-bold">Alarm Manager</h1>
      </div>
      <button className="btn btn-primary" onClick={addAlarm}>
        Add Alarm
      </button>
    </nav>

      <div className="p-6 bg-base-300 min-h-full mt-4 rounded-2xl text-center space-y-6">
        <div className="space-y-4">
          {alarms && alarms.length > 0 ? (
            alarms.map((alarm) => (
              <Alarm 
              key={alarm.id}
              time={alarm.time}
              active={alarm.active}
              days={alarm.weekdays} 
              id={alarm.id} 
              onDelete={deleteAlarm} 
              />
            ))
          ) : (
            <p className="text-lg">No alarms added yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Hero;
