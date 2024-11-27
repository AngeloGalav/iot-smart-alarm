import React, { useState } from "react";

const SettingsModal = ({
  isOpen,
  onClose,
  onSaveSettings,
  onDeleteAllAlarms,
  onSetAllAlarmsOff,
  onStopActiveAlarm,
  onResetDevice,
}) => {
  const [isClosing, setIsClosing] = useState(false);

  const [angryMode, setAngryMode] = useState(false);
  const [esp32Ip, setEsp32Ip] = useState("");

  const handleClose = () => {
    setIsClosing(true); // trigger closing animation
    setTimeout(() => {
      setIsClosing(false); // reset closing state
      onClose(); // call parent-provided onClose after animation ends
    }, 300); // match the duration of the animation
  };

  const handleSave = () => {
    onSaveSettings({ angryMode, esp32Ip });
    handleClose();
  };

  return (
    <>
      {/* Modal Overlay */}
      <div
        className={`fixed inset-0 z-50 bg-black bg-opacity-50 transition-opacity duration-300 ${
          isOpen && !isClosing
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
        onClick={handleClose}
      />

      {/* Modal Content */}
      <div
        className={`fixed z-50 left-1/2 top-1/2 transform transition-all duration-300 ${
          isOpen && !isClosing
            ? "-translate-x-1/2 -translate-y-1/2 scale-100 opacity-100"
            : "-translate-x-1/2 translate-y-full scale-90 opacity-0"
        } bg-gray-800 text-gray-200 rounded-lg shadow-lg w-full max-w-lg p-6`}
      >
        <h2 className="text-2xl font-bold mb-4">Settings</h2>
        <div className="space-y-4">
          {/* Angry Mode Toggle */}
          <div className="form-control">
            <label className="label cursor-pointer justify-between">
              <span className="label-text text-gray-200">Enable Angry Mode</span>
              <input
                type="checkbox"
                className="toggle toggle-accent"
                checked={angryMode}
                onChange={() => setAngryMode(!angryMode)}
              />
            </label>
          </div>

          {/* ESP32 Device IP Input */}
          <div className="form-control">
            <label className="label">
              <span className="label-text text-gray-200">ESP32 Device IP</span>
            </label>
            <input
              type="text"
              className="input input-bordered bg-gray-700 text-gray-200"
              placeholder="192.168.x.x"
              value={esp32Ip}
              onChange={(e) => setEsp32Ip(e.target.value)}
            />
          </div>

          {/* Delete All Alarms */}
          <div className="form-control">
            <button
              className="btn btn-error w-full"
              onClick={onDeleteAllAlarms}
            >
              Delete All Alarms
            </button>
          </div>

          {/* Set All Alarms Off */}
          <div className="form-control">
            <button
              className="btn btn-warning w-full"
              onClick={onSetAllAlarmsOff}
            >
              Set All Alarms Off
            </button>
          </div>

          {/* Stop Current Active Alarm */}
          <div className="form-control">
            <button
              className="btn btn-primary w-full"
              onClick={onStopActiveAlarm}
            >
              Stop Active Alarm
            </button>
          </div>

          {/* Reset Device */}
          <div className="form-control">
            <button
              className="btn btn-secondary w-full"
              onClick={onResetDevice}
            >
              Reset Device
            </button>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="mt-6 flex justify-between">
          <button className="btn btn-outline" onClick={handleClose}>
            Close
          </button>
          <button className="btn btn-success" onClick={handleSave}>
            Save Settings
          </button>
        </div>
      </div>
    </>
  );
};

export default SettingsModal;
