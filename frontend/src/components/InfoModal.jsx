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
  const [location, setLocation] = useState("Bologna");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inputLocation, setInputLocation] = useState("Bologna");


  const grafanaAddress = process.env.REACT_APP_GRAFANA_ADDRESS || 'localhost:3001';

  const fetchData = async () => {
    if (isOpen) {
      try {
        const weatherData = await api.getWeather();
        const delayData = await api.getDelay();
        const sleepData = await api.getSleepData();
        setWeather(weatherData.weather);
        setDelay(delayData.delay.toFixed(2));
        if (sleepData !== null) {
          setHoursSlept(sleepData.sleep);
        }
      } catch (error) {
        console.error("Error setting information:", error);
      }
    }
  };

  // fetch data each time the modal opensUp
  useEffect(() => {
    fetchData();
  }, [isOpen])


  const updateWeatherLocation = async () => {
    if (!inputLocation.trim()) return; // Prevent empty submissions
    setIsSubmitting(true);

    try {
      // Call a geocoding API to get latitude and longitude
      const geocodeResponse = await fetch(
        `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(inputLocation)}&count=1&language=en&format=json`
      );
      const geocodeData = await geocodeResponse.json();

      if (!geocodeData || !geocodeData.results || geocodeData.results.length === 0) {
        throw new Error("Location not found.");
      }

      const weather_location = {
        latitude : geocodeData.results[0].latitude,
        longitude : geocodeData.results[0].longitude,
      };

      // Send latitude and longitude to the server
      await api.updateLocation(weather_location);

      // Update the location state to reflect the new set location
      setLocation(inputLocation);

      console.info(`Updated weather location to: ${weather_location}`);
    } catch (error) {
      console.error("Error updating weather location:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

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

        {/* Grafana dashboard Input */}
        <iframe
          title="Grafana Dashboard Display"
          src={`http://${grafanaAddress}/d-solo/iot-dashboard/iot-dashboards?orgId=1&timezone=browser&refresh=5s&panelId=1&__feature.dashboardSceneSolo&from=now-30m&to=now`}
          className="w-full"
          height="200"
        ></iframe>


        {/* Weather Location Input */}
        <div className="my-6 flex items-center space-x-4">
          <label htmlFor="location" className="text-lg">
            Weather Location:
          </label>
          <input
            type="text"
            id="location"
            value={inputLocation}
            onChange={(e) => setInputLocation(e.target.value)}
            placeholder="Enter location"
            className="input input-bordered w-full max-w-xs"
          />
          <button
            onClick={async () => {
              await updateWeatherLocation(); // First update the location
              await fetchData(); // Then fetch the updated data
            }}
            className={`btn btn-primary`}
          >
            Update
          </button>
        </div>

        {/* Display the currently set location */}
        <div className="text-lg text-gray-400">
          {isSubmitting ? (
            // spinner animation when `isSubmitting` is true
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-t-transparent border-gray-400 rounded-full animate-spin"></div>
              <span>Updating Location...</span>
            </div>
          ) : (
            // display the current location when its not submitting anymore
            location && <span>Current Location: {location}</span>
          )}
        </div>

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
