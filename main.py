from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from gpiozero import LED, Button
import time
from time import sleep
import psycopg2
import sys
from dotenv import load_dotenv
import os

load_dotenv() 

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

if not all(DB_CONFIG.values()):
    print("ERRO: As credenciais do banco de dados n�o foram carregadas corretamente do .env. Verifique o arquivo .env.")
    sys.exit(1)

RELE_PIN = 21
RED_LED_PIN = 16
BUTTON_PIN = 20

rele = LED(RELE_PIN)
red_led = LED(RED_LED_PIN)
btn = Button(BUTTON_PIN)

GPIO.setwarnings(False)

leitor = SimpleMFRC522()

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def known_tag_exists(conn, tag_id: str) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM known_ids WHERE values = %s LIMIT 1", (tag_id,))
            return cur.fetchone() is not None
    except Exception:
        raise


def add_known_tag(conn, tag_id: str, desc: str):
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO known_ids (values, description) VALUES (%s, %s)", (tag_id, desc))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def log_access(conn, timestamp: float, tag_id: int, tag_text: str, access: str):
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO access_attempts (time, tag_id, tag_text, access) VALUES (%s, %s, %s, %s)",
                (timestamp, tag_id, tag_text, access),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def handle_tag(tag_id: int, text: str):
    text = text.replace("\x00", "").strip()
    seconds = float(time.time())
    read_id = str(tag_id)
    description = f"Name: {text}"

    conn = None
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"DB connection error: {e}")
        return

    try:
        if known_tag_exists(conn, read_id):
            rele.on()
            access = "authorized"
            print("Access Authorized!")
            try:
                print("Saving attempt to Database...")
                log_access(conn, seconds, tag_id, text, access)
                print("Completed!")
            except Exception as e:
                print(f"Failed saving access attempt: {e}")
            sleep(5)
            rele.off()
        else:
            if btn.is_pressed:
                red_led.on()
                try:
                    print("Add tag to the system...")
                    add_known_tag(conn, read_id, description)
                    print("Completed!")
                except Exception as e:
                    print(f"Failed to add known tag: {e}")
                finally:
                    red_led.off()
                    sleep(2)
            else:
                for _ in range(5):
                    red_led.on()
                    sleep(0.2)
                    red_led.off()
                    sleep(0.2)
                access = "denied"
                print("Access Denied!")
                try:
                    print("Saving attempt to Database...")
                    log_access(conn, seconds, tag_id, text, access)
                    print("Completed!")
                except Exception as e:
                    print(f"Failed saving access attempt: {e}")
    except Exception as e:
        print(f"Error while handling tag: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    print("Starting RFID reader. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                tag_id, text = leitor.read()
            except Exception as e:
                print(f"Reader error: {e}")
                sleep(1)
                continue

            handle_tag(tag_id, text)

    except KeyboardInterrupt:
        print("Exiting, cleaning up GPIO...")
    finally:
        try:
            rele.off()
            red_led.off()
            GPIO.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    main()