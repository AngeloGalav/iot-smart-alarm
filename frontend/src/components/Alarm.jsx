import React, { useState, useEffect } from "react";

const Alarm = ({ id, onDelete }) => {
  const [isAlarmOn, setIsAlarmOn] = useState(false);
  const [alarmTime, setAlarmTime] = useState("00:00");
  const [selectedDays, setSelectedDays] = useState(new Set());

  const handleToggle = () => setIsAlarmOn(!isAlarmOn);
  const handleTimeChange = (e) => setAlarmTime(e.target.value);

  const weekdays = [
    { label: "M", id: 1, name: "Monday" },
    { label: "T", id: 2, name: "Tuesday" },
    { label: "W", id: 3, name: "Wednesday" },
    { label: "T", id: 4, name: "Thursday" },
    { label: "F", id: 5, name: "Friday" },
    { label: "S", id: 6, name: "Saturday" },
    { label: "S", id: 7, name: "Sunday" },
  ];

  // Handle toggling of selected days
  const handleDayClick = (dayId) => {
    // react automatically sends the prevstate as parameter to the anon func
    // this happens each time we use an updater from the useState hook
    setSelectedDays((prevDays) => {
      const updatedDays = new Set(prevDays);
      // add to the set only if it is not the in the prevDays list, 
      updatedDays.has(dayId) ? updatedDays.delete(dayId) : updatedDays.add(dayId);
      return updatedDays;
    });
  };

  // This stuff will be handled by the module in due time
  // runs each time [isAlarmOn, alarmTime] changes
  useEffect(() => {
    const interval = setInterval(() => {
      const currentTime = new Date();
      // get current time
      const formattedCurrentTime = `${String(currentTime.getHours()).padStart(2, '0')}:${String(
        currentTime.getMinutes()
      ).padStart(2, '0')}`;
      // if current time is qual alarmTime, then ring!
      if (isAlarmOn && formattedCurrentTime === alarmTime) {
        alert("Alarm Ringing!");
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isAlarmOn, alarmTime]);

  return (
    <div className="p-4 my-2 bg-base-200 rounded-xl shadow-md space-y-4 text-center">
      <div className="flex justify-between items-center">
        {/* ALarm title */}
        <h2 className="text-xl font-bold">Alarm {id}</h2>

        {/* Weekday Selection */}
        <div className="flex space-x-2">
          {weekdays.map(({ label, id }) => (
            <button
              key={id}
              className={`w-10 h-10 flex items-center justify-center rounded-full border font-bold ${
                selectedDays.has(id) ? "bg-teal-500 text-white border-blue-700" : "bg-gray-700 text-gray-100 border-gray-800"
              }`}
              onClick={() => handleDayClick(id)}
            >
              {label}
            </button>
          ))}
        </div>
          
        {/* Delete button */}
        <button className="btn btn-error btn-sm" onClick={() => onDelete(id)}>
          Delete
        </button>
      </div>
      
      {/* handle time change */}
      <div className="form-control">
        <label className="label">
          <span className="label-text">Set Alarm Time:</span>
        </label>
        <input
          type="time"
          className="input input-bordered w-full"
          value={alarmTime}
          onChange={handleTimeChange}
        />
      </div>

      <div className="form-control">
        <label className="label cursor-pointer justify-center">
          <span className="label-text mr-2">Alarm Status:</span>
          <input
            type="checkbox"
            className="toggle toggle-primary"
            checked={isAlarmOn}
            onChange={handleToggle}
          />
        </label>
      </div>

      <p className="text-lg">
        Alarm is <span className={isAlarmOn ? "text-green-500" : "text-red-500"}>{isAlarmOn ? "On" : "Off"}</span>
      </p>
      <p className="text-lg">Alarm set for: {alarmTime}</p>
    </div>
  );
};

export default Alarm;
