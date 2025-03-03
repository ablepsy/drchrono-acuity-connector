# DrChrono-Acuity Connector

This project provides a robust integration between DrChrono and Acuity Scheduling for seamless appointment synchronization and patient management.

## Features

- **Bidirectional Appointment Syncing**: Automatically sync appointments between DrChrono and Acuity in both directions
- **Patient Data Management**: Create and update patient records across both platforms
- **Intelligent Deduplication**: Avoid duplicate appointments when syncing between systems
- **Configurable Sync Settings**: Control sync frequency and date range
- **Comprehensive Logging**: Detailed logs for troubleshooting and auditing

## Prerequisites

- DrChrono API credentials (API key)
- Acuity Scheduling API credentials (User ID and API key)
- Python 3.7+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/drchrono-acuity-connector.git
   cd drchrono-acuity-connector
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   - Copy the `config.json.example` file to `config.json`
   - Add your DrChrono and Acuity API credentials

   Alternatively, you can use environment variables:
   - Copy the `.env.example` file to `.env`
   - Add your API credentials to the `.env` file

## Usage

### Running the Connector

```
python main.py
```

The connector will start running in continuous mode, syncing appointments at the configured interval.

### Configuration Options

Edit `config.json` or set environment variables to configure:

- `drchrono_api_key`: Your DrChrono API key
- `acuity_user_id`: Your Acuity user ID
- `acuity_api_key`: Your Acuity API key
- `sync_interval`: How often to sync (in minutes)
- `days_to_sync`: How many days into the future to sync

## Deployment

This connector can be deployed as a service on any server or cloud platform that supports Python.

### Deploying to Heroku

1. Make sure you have the Heroku CLI installed
2. Login to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

4. Set environment variables:
   ```
   heroku config:set DRCHRONO_API_KEY=your_api_key
   heroku config:set ACUITY_USER_ID=your_user_id
   heroku config:set ACUITY_API_KEY=your_api_key
   heroku config:set SYNC_INTERVAL=60
   heroku config:set DAYS_TO_SYNC=30
   ```

5. Deploy your application:
   ```
   git push heroku main
   ```

## How It Works

The connector performs the following operations:

1. Authenticates with both DrChrono and Acuity APIs
2. Fetches appointments from both systems within the configured date range
3. Compares appointments to identify new ones that need to be synced
4. Converts appointment data between formats
5. Creates new appointments in the target system
6. Handles patient information, creating new patient records if needed
7. Logs all activities for auditing and troubleshooting

## API Reference

### DrChrono API

The connector uses the following DrChrono API endpoints:
- `/api/users/current` - Authentication
- `/api/appointments` - Appointment management
- `/api/patients` - Patient management

### Acuity API

The connector uses the following Acuity API endpoints:
- `/api/v1/users/{user_id}` - Authentication
- `/api/v1/appointments` - Appointment management
- `/api/v1/appointment-types` - Appointment type mapping

## Troubleshooting

Check the `connector.log` file for detailed log information if you encounter any issues.

Common issues:
- API authentication failures: Verify your API credentials
- Appointment sync failures: Check API rate limits and data format compatibility
- Patient data mismatch: Review the patient mapping logic in the code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
