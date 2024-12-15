"""
Telegram bot which allows to be run etc...
"""
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, Updater, CommandHandler, CallbackContext, Application, ContextTypes
import requests
from telegram_secrets import TELEGRAM_BOT_TOKEN
import os
import re

backend_host = os.getenv("BACKEND_HOST", "localhost")
backend_port = os.getenv("BACKEND_PORT", "5000")


BACKEND_URL = f"http://localhost:5000"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_time_format(time_str):
    match = re.match(r"^([01]?\d|2[0-3]):([0-5]?\d)$", time_str)
    if match:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your Alarm Bot. Here are the commands you can use:\n"
                              "/add_alarm HH:MM weekdays (e.g., /add_alarm 07:30 1,2,3)\n"
                              "/delete_alarm <alarm_id>\n"
                              "/toggle_alarm <alarm_id>\n"
                              "/update_alarm <alarm_id> HH:MM weekdays\n"
                              "/stop_alarm\n"
                              "/list_alarms")

async def add_alarm(update: Update, context: CallbackContext):
    try:
        args = context.args

        if len(args) < 1:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Usage: /add_alarm HH:MM [weekdays (optional)]\n"
                     "e.g., /add_alarm 07:30 1,2,3\n"
                     "If no weekdays are provided, the alarm will be set for all days."
            )
            return

        # if provided, check that format time is right using a regular expr.
        time = args[0]
        if not is_valid_time_format(time):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Invalid time format. Please provide a valid time in HH:MM format (e.g., 07:30)."
            )
            return

        # if provided, check weekdays sanity
        weekdays = []
        if len(args) > 1:
            weekdays_str = args[1].split(",")
            try:
                weekdays = [int(day) for day in weekdays_str]
                if any(day < 1 or day > 7 for day in weekdays):
                    raise ValueError("Weekdays must be numbers from 1 to 7.")
                if len(set(weekdays)) != len(weekdays):
                    raise ValueError("Weekdays must not contain duplicates.")

                weekdays = [day - 1 for day in weekdays]

            except ValueError as e:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Invalid weekdays: {e}. Please use numbers from 1 to 7 without duplicates."
                )
                return

        # send data to server
        payload = {"time": time, "weekdays": weekdays}
        response = requests.post(f"{BACKEND_URL}/alarms", json=payload)

        if response.status_code == 201:
            alarm = response.json()["alarm"]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Alarm added successfully!\nID: {alarm['id']}\nTime: {alarm['time']}\nWeekdays: {', '.join(map(str, [day + 1 for day in alarm['weekdays']]))}"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Error adding alarm: {response.json().get('message', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Error in add_alarm: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while adding the alarm."
        )

async def delete_alarm(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) != 1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /delete_alarm <alarm_id>")
            return

        alarm_id = int(args[0])
        response = requests.delete(f"{BACKEND_URL}/alarms/{alarm_id}")

        if response.status_code == 200:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Alarm {alarm_id} deleted successfully!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,text=f"Error deleting alarm: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error in delete_alarm: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,text="An error occurred while deleting the alarm.")

async def update_alarm(update: Update, context: CallbackContext):
    try:
        args = context.args

        if len(args) < 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Usage: /update_alarm <alarm_id> [HH:MM] [weekdays]\n"
                     "Provide either or both of HH:MM and weekdays (e.g., /update_alarm 1 07:30 1,2,3)."
            )
            return

        # parse alarm id
        try:
            alarm_id = int(args[0])
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Invalid alarm ID. Please provide a valid numeric alarm ID."
            )
            return

        payload = {}

        # check if time is correct format
        if len(args) > 1 and ":" in args[1]: # allow only weekdays change if input is not time
            time = args[1]
            if not is_valid_time_format(time):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Invalid time format. Please provide a valid time in HH:MM format (e.g., 07:30)."
                )
                return
            payload["time"] = time

        # check if time is correct format
        if len(args) > 2:
            weekdays_str = args[2].split(",")
            try:
                weekdays = [int(day) for day in weekdays_str]
                if any(day < 1 or day > 7 for day in weekdays):
                    raise ValueError("Weekdays must be numbers from 1 to 7.")
                if len(set(weekdays)) != len(weekdays):
                    raise ValueError("Weekdays must not contain duplicates.")

                # Convert weekdays from 1-7 to 0-6 for the backend
                weekdays = [day - 1 for day in weekdays]
                payload["weekdays"] = weekdays

            except ValueError as e:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Invalid weekdays: {e}. Please use numbers from 1 to 7 without duplicates."
                )
                return

        # ensure at least one field is being updated
        if not payload:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Error: You must provide at least one field to update (time or weekdays)."
            )
            return

        # send the update request to the backend
        response = requests.put(f"{BACKEND_URL}/alarms/{alarm_id}", json=payload)

        if response.status_code == 200:
            updated_fields = ", ".join(f"{key}: {value}" for key, value in payload.items())
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Alarm {alarm_id} updated successfully with changes: {updated_fields}"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Error updating alarm: {response.json().get('message', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Error in update_alarm: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while updating the alarm."
        )


async def stop_alarm(update: Update, context: CallbackContext):
    try:
        response = requests.post(f"{BACKEND_URL}/stop_alarm")
        if response.status_code == 200:
            await context.bot.send_message(chat_id=update.effective_chat.id,text="Alarm stopped successfully!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,text=f"Error stopping alarm: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error in stop_alarm: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,text="An error occurred while stopping the alarm.")

async def list_alarms(update: Update, context: CallbackContext):
    try:
        response = requests.get(f"{BACKEND_URL}/alarms")
        if response.status_code == 200:
            alarms = response.json()
            if alarms:
                message = "Current Alarms:\n"
                for alarm in alarms:
                    message += f"ID: {alarm['id']}, Time: {alarm['time']}, Weekdays: [{','.join(map(str, alarm['weekdays']))}], Active: {alarm['active']}\n"
                await context.bot.send_message(chat_id=update.effective_chat.id,text=message)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,text="No alarms set.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,text=f"Error listing alarms: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error in list_alarms: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,text="An error occurred while listing the alarms.")

async def toggle_alarm(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) != 1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /toggle_alarm <alarm_id>")
            return
        alarm_id = int(args[0])
        response = requests.patch(f"{BACKEND_URL}/alarms/{alarm_id}/toggle")

        if response.status_code == 200:
            alarm = response.json()["alarm"]
            status = "enabled" if alarm["active"] else "disabled"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Alarm {alarm_id} toggled successfully! New status: {status}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error toggling alarm: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error in toggle_alarm: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while toggling the alarm.")


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_alarm", add_alarm))
    application.add_handler(CommandHandler("delete_alarm", delete_alarm))
    application.add_handler(CommandHandler("update_alarm", update_alarm))
    application.add_handler(CommandHandler("stop_alarm", stop_alarm))
    application.add_handler(CommandHandler("list_alarms", list_alarms))
    application.add_handler(CommandHandler("toggle_alarm", toggle_alarm))

    application.run_polling()

if __name__ == "__main__":
    main()
