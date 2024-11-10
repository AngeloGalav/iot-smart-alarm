import React, { useState } from "react";
import Alarm from "./Alarm";
import "./Hero.css"

const Hero = () => {
  const [alarms, setAlarms] = useState([]);

  const addAlarm = () => {
    const newId = alarms.length + 1;
    // adds a new element to the alarm array
    setAlarms([...alarms, { id: newId }]);
  };

  const deleteAlarm = (id) => {
    setAlarms(alarms.filter((alarm) => alarm.id !== id));
  };

  return (
    <div>
      <nav className="my-navbar m-1">
      <div>
      <h1 className="text-3xl font-bold">Alarm Manager</h1>
      </div>
      <button className="btn btn-primary" onClick={addAlarm}>
        Add Alarm
      </button>
    </nav>

      <div className="p-6 bg-base-300 min-h-screen text-center space-y-6">
        <div className="space-y-4">
          {alarms.length > 0 ? (
            alarms.map((alarm) => (
              <Alarm key={alarm.id} id={alarm.id} onDelete={deleteAlarm} />
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
