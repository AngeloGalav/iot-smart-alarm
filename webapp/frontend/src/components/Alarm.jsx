import React, { useState, useEffect } from "react";

const Alarm = ({ id, onDelete }) => {
  const [isAlarmOn, setIsAlarmOn] = useState(false);
  const [alarmTime, setAlarmTime] = useState("00:00");

  const handleToggle = () => setIsAlarmOn(!isAlarmOn);
  const handleTimeChange = (e) => setAlarmTime(e.target.value);

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
        <h2 className="text-xl font-bold">Alarm {id}</h2>
        <button className="btn btn-error btn-sm" onClick={() => onDelete(id)}>
          Delete
        </button>
      </div>
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
