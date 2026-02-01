# Raspberry Pi RFID Access Control System

A Python-based RFID access control system for Raspberry Pi using the MFRC522 reader. This project allows you to manage access control with RFID tags, storing authorized tags and access logs in a PostgreSQL database.

## Features

- 🔓 **RFID Tag Authentication** - Read and validate RFID tags
- 📝 **Access Logging** - Log all access attempts (authorized/denied) to PostgreSQL
- ➕ **Dynamic Tag Registration** - Add new authorized tags using a physical button
- 💡 **LED Indicators** - Visual feedback for access status
- 🔌 **Relay Control** - Trigger a relay (e.g., door lock) on successful authentication

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- MFRC522 RFID Reader
- RFID Tags/Cards (13.56 MHz)
- Relay Module (connected to GPIO 21)
- Red LED (connected to GPIO 16)
- Push Button (connected to GPIO 20)

### Wiring Diagram

| Component    | GPIO Pin |
|--------------|----------|
| Relay        | 21       |
| Red LED      | 16       |
| Button       | 20       |
| MFRC522      | SPI (default pins) |

## Software Requirements

- Python 3.7+
- PostgreSQL database
- Docker & Docker Compose (optional, for local database)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/raspberrypi-rfid.git
cd raspberrypi-rfid
```

### 2. Install Python Dependencies

```bash
pip install mfrc522 RPi.GPIO gpiozero psycopg2-binary python-dotenv
```

### 3. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
sudo reboot
```

### 4. Configure Environment Variables

Copy the example environment file and edit it with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` with your database configuration:

```env
DB_HOST=localhost
DB_DATABASE=rfid_access
DB_USER=your_username
DB_PASSWORD=your_password
```

### 5. Set Up the Database

#### Option A: Using Docker Compose (Recommended for Development)

Add the following to your `.env` file for pgAdmin:

```env
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin_password
```

Start the PostgreSQL and pgAdmin containers:

```bash
docker-compose up -d
```

Access pgAdmin at `http://localhost:5050` to manage your database.

#### Option B: Using an Existing PostgreSQL Instance

Connect to your PostgreSQL server and create the required tables:

```bash
psql -h your_host -U your_user -d your_database -f tables.sql
```

Or run the SQL manually:

```sql
CREATE TABLE known_ids (
    registration_id SERIAL PRIMARY KEY, 
    values BIGINT NOT NULL UNIQUE, 
    description VARCHAR(255) 
);

CREATE TABLE access_attempts (
    log_id SERIAL PRIMARY KEY, 
    time NUMERIC(15, 6) NOT NULL, 
    tag_id BIGINT, 
    tag_text VARCHAR(255), 
    access VARCHAR(50) NOT NULL
);
```

## Usage

### Running the Application

```bash
python main.py
```

The system will start and wait for RFID tags to be scanned.

### Access Control Behavior

| Scenario | Action | Indicator |
|----------|--------|-----------|
| **Known Tag** | Relay activates for 5 seconds | Access granted |
| **Unknown Tag** | Access denied | Red LED blinks 5 times |
| **Unknown Tag + Button Pressed** | Tag is registered | Red LED stays on during registration |

### Registering New Tags

1. Press and hold the **registration button** (GPIO 20)
2. Scan the new RFID tag
3. The red LED will light up while the tag is being registered
4. Release the button after registration completes

### Stopping the Application

Press `Ctrl+C` to gracefully stop the application and clean up GPIO resources.

## Database Schema

### `known_ids` Table

Stores authorized RFID tags.

| Column          | Type         | Description                    |
|-----------------|--------------|--------------------------------|
| registration_id | SERIAL       | Primary key                    |
| values          | BIGINT       | Unique RFID tag ID             |
| description     | VARCHAR(255) | Tag description (e.g., owner)  |

### `access_attempts` Table

Logs all access attempts.

| Column   | Type          | Description                        |
|----------|---------------|------------------------------------|
| log_id   | SERIAL        | Primary key                        |
| time     | NUMERIC(15,6) | Unix timestamp of attempt          |
| tag_id   | BIGINT        | RFID tag ID                        |
| tag_text | VARCHAR(255)  | Text stored on the tag             |
| access   | VARCHAR(50)   | Result: "authorized" or "denied"   |

## Troubleshooting

### Common Issues

**SPI not enabled:**
```bash
ls /dev/spi*
# If no output, enable SPI via raspi-config
```

**Database connection failed:**
- Verify your `.env` file has correct credentials
- Ensure PostgreSQL is running and accessible
- Check firewall rules if using a remote database

**MFRC522 not detected:**
- Verify wiring connections
- Ensure SPI is enabled
- Check if the reader is powered correctly

## License

This project is open source and available under the MIT License.
