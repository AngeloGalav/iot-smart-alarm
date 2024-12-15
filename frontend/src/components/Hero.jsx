import React, { useState, useEffect } from "react";
import Alarm from "./Alarm";
import api from "../api";
import "./Hero.css"
import SettingsModal from "./SettingsModal";
import InfoModal from "./InfoModal";
import { FaGear } from "react-icons/fa6";
import { BsClipboardDataFill } from "react-icons/bs";

const Hero = () => {
  const [alarms, setAlarms] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDataModalOpen, setDataIsModalOpen] = useState(false);

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
      console.log(alarms, data.alarm)
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
      <h1 className="text-3xl font-bold">alarm-thingy Manager</h1>
      </div>
      <div className="grid gap-4 grid-cols-4">
      <button className="btn btn-accent col-span-2" onClick={addAlarm}>
        Add Alarm
      </button>
      <button className="btn btn-secondary" onClick={() => setDataIsModalOpen(true)}>
        <BsClipboardDataFill />
      </button>
      <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
        <FaGear />
      </button>
      </div>
    </nav>

    <SettingsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onDeleteAllAlarms={() => alert("not implemented")}
      />
    
    <InfoModal
        isOpen={isDataModalOpen}
        onClose={() => setDataIsModalOpen(false)}
      />

      <div className="p-6 bg-base-300 min-h-full mt-4 mb-4 rounded-2xl text-center space-y-6">
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
