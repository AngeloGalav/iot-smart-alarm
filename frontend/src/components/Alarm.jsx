import React, { useState, useEffect } from "react";
import api from "../api";

const Alarm = ({ id, time, days, active, onDelete}) => {
  const [isAlarmOn, setIsAlarmOn] = useState(false);
  const [alarmTime, setAlarmTime] = useState("08:00");
  const [selectedDays, setSelectedDays] = useState(new Set());
  const weekdays = [
    { label: "M", id: 1, name: "Monday" },
    { label: "T", id: 2, name: "Tuesday" },
    { label: "W", id: 3, name: "Wednesday" },
    { label: "T", id: 4, name: "Thursday" },
    { label: "F", id: 5, name: "Friday" },
    { label: "S", id: 6, name: "Saturday" },
    { label: "S", id: 7, name: "Sunday" },
  ];

  // handles alarm toggle by making a request
  const handleToggle = async () => {
    try {
      const updatedAlarm = await api.toggleAlarm(id);
      setIsAlarmOn(updatedAlarm.alarm.active);
    } catch (error) {
      console.error(`Error toggling alarm with id ${id} : ${error}`);
    }
  };

  // handles alarm time change by making a request
  const handleTimeChange = async (e) => {
    const newTime = e.target.value;
    setAlarmTime(newTime);
    try {
      await api.updateAlarm(id, { time: newTime });
    } catch (error) {
      console.error(`Error changing time for alarm id ${id} : ${error}`);
    }
  };

  // handles weekday modification by making a request
  const handleDayClick = async (dayId) => {
    setSelectedDays((prevDays) => {
      const updatedDays = new Set(prevDays);
      updatedDays.has(dayId) ? updatedDays.delete(dayId) : updatedDays.add(dayId);

      const updatedDayNames = Array.from(updatedDays).map(
        (id) => weekdays.find((w) => w.id === id)?.name
      );

      api.updateAlarm(id, { weekdays: updatedDayNames }).catch((error) =>
        console.error(`Error changing weekday for alarm id ${id} : ${error}`)
      );

      return updatedDays;
    });
  };


  useEffect(() => {
    if (!id) return;
    const fetchAlarmData = async () => {
      try {
        console.log(time, days, active)
        setAlarmTime(time);
        setSelectedDays(new Set(days.map((day) => weekdays.find((w) => w.name === day)?.id)));
        setIsAlarmOn(active);
      } catch (error) {
        console.error(`Error fetching alarm data for id ${id} : ${error}`);
      }
    };
    fetchAlarmData();
  }, [id]);

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
