import React, { useState } from "react";
import api from "../api";

const SettingsModal = ({
  isOpen,
  onClose,
  onDeleteAllAlarms
}) => {
  const [isClosing, setIsClosing] = useState(false);
  const [angryMode, setAngryMode] = useState(false);
  const [useMQTT, setUseMQTT] = useState(false);
  const [useAsyncHTTP, setUseAsyncHTTP] = useState(false);
  const [samplingRate, setSamplingRate] = useState(1);
  const [windowSize, setWindowSize] = useState(10);
  const [samplingRateError, setSamplingRateError] = useState("");
  const [wSizeError, setWSizeError] = useState("");
  const [volume, setVolume] = useState(20);


  // Stop the active alarm
  const stopActiveAlarm = async () => {
    try {
      await api.stopAlarm();
      console.log("Active alarm stopped");
    } catch (error) {
      console.error("Error stopping active alarm:", error);
    }
  };

  const validateSamplingRate = () => {
    const rate = parseFloat(samplingRate);
    if (rate < 0.01 || rate > 10) {
      setSamplingRateError("Sampling rate must be between 0.01 and 10.");
      return false;
    }
    setSamplingRateError("");
    return true;
  };

  const validateWSize = () => {
    const rate = parseFloat(windowSize);
    if (rate <= 0) {
      setWSizeError("Window size must be a positive number (integers will be rounded)");
      return false;
    }
    setWSizeError("");
    return true;
  };


  const sendSamplingRate = async () => {
    if (!validateSamplingRate()) return;

    try {
      await api.sendSamplingRate({ sampling_rate: parseFloat(samplingRate) });
      console.log("Sampling rate sent successfully");
    } catch (error) {
      console.error("Error sending sampling rate:", error);
    }
  };

  // Save settings from modal
  const saveSettings = async () => {
    if (!validateSamplingRate()) return;
    if (!validateWSize()) return;

    const settings = {
      command: "settings",
      use_mqtt: useMQTT,
      use_async_http: useAsyncHTTP,
      angry_mode: angryMode,
      sampling_rate: samplingRate,
      w_size : windowSize,
      vol : volume
    };

    try {
      await api.sendSettings(settings);
      console.log("Settings saved successfully:", settings);
    } catch (error) {
      console.error("Error saving settings:", error);
    }
  }

  const handleClose = () => {
    setIsClosing(true); // trigger closing animation
    setTimeout(() => {
      setIsClosing(false); // reset closing state
      onClose(); // call parent-provided onClose after animation ends
    }, 300); // match the duration of the animation
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
          {/* MQTT Toggle */}
          <div className="form-control">
            <label className="label cursor-pointer justify-between">
              <span className="label-text text-gray-200">Use MQTT instead of HTTP for Data Transmission</span>
              <input
                type="checkbox"
                className="toggle toggle-accent"
                checked={useMQTT}
                onChange={() => setUseMQTT(!useMQTT)}
              />
            </label>
          </div>
          {/* Async HTTP Toggle */}
          <div className="form-control">
            <label className="label cursor-pointer justify-between">
              <span className="label-text text-gray-200">Use Asynchronous HTTP</span>
              <input
                type="checkbox"
                className="toggle toggle-accent"
                checked={useAsyncHTTP}
                onChange={() => setUseAsyncHTTP(!useAsyncHTTP)}
              />
            </label>
          </div>

          {/* ESP32 Sampling Rate */}
          <div className="form-control">
            <label className="label">
              <span className="label-text text-gray-200">ESP32 Sampling Rate</span>
            </label>
            <input
              type="text"
              className={`input input-bordered ${
                samplingRateError ? "border-red-500" : "bg-gray-700"
              } text-gray-200`}
              placeholder="1"
              value={samplingRate}
              onChange={(e) => setSamplingRate(e.target.value)}
            />
            {samplingRateError && (
              <span className="text-red-500 text-sm mt-1">
                {samplingRateError}
              </span>
            )}
          </div>

          {/* Moving Avg Window Size */}
          <div className="form-control">
            <label className="label">
              <span className="label-text text-gray-200">Moving Average Window Size</span>
            </label>
            <input
              type="text"
              className={`input input-bordered ${
                wSizeError ? "border-red-500" : "bg-gray-700"
              } text-gray-200`}
              placeholder="1"
              value={windowSize}
              onChange={(e) => setWindowSize(e.target.value)}
            />
            {wSizeError && (
              <span className="text-red-500 text-sm mt-1">
                {wSizeError}
              </span>
            )}
          </div>

          {/* Volume Slider */}
          <div className="form-control">
            <label className="label">
              <span className="label-text text-gray-200">Alarm Volume</span>
            </label>
            <input
              type="range"
              min="0"
              max="50"
              value={volume}
              className="range range-primary"
              onChange={(e) => setVolume(Number(e.target.value))}
            />
            <div className="text-center text-gray-200">{volume}</div>
          </div>


          {/* Stop Current Active Alarm */}
          <div className="form-control mt-4">
            <button
              className="btn btn-warning w-full"
              onClick={stopActiveAlarm}
            >
              Stop Active Alarm
            </button>
          </div>

          {/* Send Sampling Rate */}
          <div className="form-control">
            <button
              className="btn btn-secondary w-full"
              onClick={sendSamplingRate}
            >
              Send Sampling Rate to ESP32
            </button>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="mt-6 flex justify-between">
          <button className="btn btn-outline" onClick={handleClose}>
            Close
          </button>
          <button className="btn btn-success" onClick={saveSettings}>
            Send Settings to ESP32
          </button>
        </div>
      </div>
    </>
  );
};

export default SettingsModal;
