import socket
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def send_broker_ip(alarm_ip, alarm_port):
    local_ip = socket.gethostbyname(socket.gethostname())
    logging.info(f"Preparing to send broker IP to ESP32 at {alarm_ip}:{alarm_port}...")

    while True:
        try:
            # create a new socket for each retry
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                logging.info("Attempting to connect to ESP32...")
                s.settimeout(10)  # timeout for connection attempts
                s.connect((alarm_ip, alarm_port))
                logging.info("Connected to ESP32")

                while True:
                    # send broker IP
                    s.sendall(local_ip.encode())
                    logging.info(f"Sent broker IP: {local_ip}")

                    # wait for ACK
                    ack = s.recv(1024)
                    if ack.decode().strip() == "ACK":
                        logging.info("ACK received. Broker IP sent successfully.")
                        return
        except socket.timeout:
            logging.error("Connection attempt timed out. Retrying...")
        except Exception as e:
            logging.error(f"Failed to send broker IP: {e}. Retrying...")
        time.sleep(5)  # retry every 5 seconds
