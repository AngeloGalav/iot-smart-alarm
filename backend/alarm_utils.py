import os
import json
import logging

def load_alarms_from_file(alarm_file):
    global alarms
    if os.path.exists(alarm_file):
        try:
            with open(alarm_file, 'r') as file:
                alarms = json.load(file)
                logging.info(f"Loaded alarms from {alarm_file}.")
        except json.JSONDecodeError:
            logging.error(f"Failed to parse {alarm_file}. Starting with empty alarms.")
            alarms = []
    else:
        logging.info(f"{alarm_file} does not exist. Starting with empty alarms.")
        alarms = []
    return alarms

def save_alarms_to_file(alarm_file, alarms):
    try:
        with open(alarm_file, 'w') as file:
            json.dump(alarms, file, indent=4)
            logging.info(f"Alarms saved to {alarm_file}.")
    except Exception as e:
        logging.error(f"Failed to save alarms to {alarm_file}: {e}")