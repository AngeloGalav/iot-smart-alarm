import React, { useState } from "react";
import Alarm from "./Alarm";

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
    <div className="p-6 bg-base-300 min-h-screen text-center space-y-6">
      <h1 className="text-3xl font-bold">Alarm Manager</h1>
      <button className="btn btn-primary" onClick={addAlarm}>
        Add Alarm
      </button>

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
  );
};

export default Hero;
