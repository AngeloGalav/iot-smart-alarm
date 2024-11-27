import React, { useState, useEffect } from "react";
import Alarm from "./Alarm";
import api from "../api";
import "./Hero.css"
import SettingsModal from "./Settings";
import { FaGear } from "react-icons/fa6";


const Hero = () => {
  const [alarms, setAlarms] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);


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

    // Delete all alarms
    const deleteAllAlarms = async () => {
      try {
        await api.deleteAllAlarms(); // Assume API endpoint exists
        setAlarms([]);
      } catch (error) {
        console.error("Error deleting all alarms:", error);
      }
    };
  
    // Set all alarms to off
    const setAllAlarmsOff = async () => {
      try {
        await api.setAllAlarmsOff(); // Assume API endpoint exists
        setAlarms((prevAlarms) =>
          prevAlarms.map((alarm) => ({ ...alarm, active: false }))
        );
      } catch (error) {
        console.error("Error setting all alarms to off:", error);
      }
    };
  
    // Stop the current active alarm
    const stopActiveAlarm = async () => {
      try {
        await api.stopActiveAlarm(); // Assume API endpoint exists
        console.log("Active alarm stopped");
      } catch (error) {
        console.error("Error stopping active alarm:", error);
      }
    };
  
    // Reset the device
    const resetDevice = async () => {
      try {
        await api.resetDevice(); // Assume API endpoint exists
        console.log("Device reset");
      } catch (error) {
        console.error("Error resetting device:", error);
      }
    };
  
    // Save settings from modal
    const saveSettings = (settings) => {
      console.log("Settings saved:", settings);
      // You can send these settings to the backend if required
    };

  return (
    <div className="flex-grow container mx-auto p-4">
      <nav className="my-navbar m-1">
      <div>
      <h1 className="text-3xl font-bold">Alarm Manager</h1>
      </div>
      <div className="grid gap-4 grid-cols-3">
      <button className="btn btn-accent col-span-2" onClick={addAlarm}>
        Add Alarm
      </button>
      <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
        <FaGear />
      </button>
      </div>
    </nav>

    <SettingsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSaveSettings={saveSettings}
        onDeleteAllAlarms={deleteAllAlarms}
        onSetAllAlarmsOff={setAllAlarmsOff}
        onStopActiveAlarm={stopActiveAlarm}
        onResetDevice={resetDevice}
      />

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
