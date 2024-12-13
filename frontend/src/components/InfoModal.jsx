import React, { useState, useEffect } from "react";
import api from "../api";
import { IoRainy } from "react-icons/io5";
import { IoMdCloudy } from "react-icons/io";
import { IoIosSunny } from "react-icons/io";
import { GiNightSleep } from "react-icons/gi";

const InfoModal = ({
  isOpen,
  onClose
}) => {
  const [isClosing, setIsClosing] = useState(false);
  const [weather, setWeather] = useState(null);
  const [delay, setDelay] = useState(null);
  const [hoursSlept, setHoursSlept] = useState(null);

  const grafanaAddress = process.env.REACT_APP_GRAFANA_ADDRESS || 'localhost:3001';

  useEffect(() => {
    const fetchData = async () => {
      if (isOpen) {
        try {
          const weatherData = await api.getWeather();
          const delayData = await api.getDelay();
          const sleepData = await api.getSleepData();
          setWeather(weatherData.weather);
          setDelay(delayData.delay.toFixed(2));
          if (sleepData !== null) {
            setHoursSlept(sleepData.sleep.toFixed(2));
          }
        } catch (error) {
          console.error("Error setting information:", error);
        }
      }
    };

    fetchData();
  }, [isOpen])


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
        } bg-gray-800 text-gray-200 rounded-lg shadow-lg w-full max-w-2xl p-6`}
      >
        <h2 className="text-2xl font-bold mb-4">Information</h2>
        {/* Modal Footer */}
        <div className={`my-6 flex justify-center w-full space-x-6 text-xl`}>
          {delay && <div>Delay: {delay} ms</div>}
          {hoursSlept && <div className="flex items-center space-x-2"><span><GiNightSleep /></span> : {hoursSlept} hours
            </div>}
          {weather && <div className="flex items-center space-x-2"><span>Weather:</span> 
            {weather === 'rainy' ? <IoRainy /> :
             weather === 'cloudy' ? <IoMdCloudy /> :
             weather === 'sunny' ? <IoIosSunny /> : null}
            </div>}
        </div>

        <iframe
          title="Grafana Dashboard Display"
          src={`http://${grafanaAddress}/d-solo/iot-dashboard/iot-dashboards?orgId=1&timezone=browser&refresh=5s&panelId=1&__feature.dashboardSceneSolo`}
          className="w-full"
          height="200"
        ></iframe>
        {/* Modal Footer */}
        <div className="mt-6 flex justify-between">
          <div></div>
          <button className="btn btn-error" onClick={handleClose}>
            Close
          </button>
        </div>
      </div>
    </>
  );
};

export default InfoModal;
