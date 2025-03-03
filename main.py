import requests
import os
import json
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("connector.log"), logging.StreamHandler()]
)
logger = logging.getLogger("drchrono-acuity-connector")

class DrChronoAcuityConnector:
    def __init__(self, drchrono_api_key, acuity_user_id, acuity_api_key):
        self.drchrono_api_key = drchrono_api_key
        self.acuity_user_id = acuity_user_id
        self.acuity_api_key = acuity_api_key
        self.drchrono_headers = {'Authorization': f'Bearer {drchrono_api_key}'}
        self.acuity_auth = (acuity_user_id, acuity_api_key)

    def authenticate_drchrono(self):
        """Authenticate with DrChrono API and return user data"""
        logger.info("Authenticating with DrChrono")
        response = requests.get('https://drchrono.com/api/users/current', headers=self.drchrono_headers)
        if response.status_code == 200:
            logger.info("DrChrono authentication successful")
            return response.json()
        else:
            error_msg = f"Failed to authenticate with DrChrono: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def authenticate_acuity(self):
        """Authenticate with Acuity API and return user data"""
        logger.info("Authenticating with Acuity")
        response = requests.get(
            f'https://acuityscheduling.com/api/v1/users/{self.acuity_user_id}', 
            auth=self.acuity_auth
        )
        if response.status_code == 200:
            logger.info("Acuity authentication successful")
            return response.json()
        else:
            error_msg = f"Failed to authenticate with Acuity: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_drchrono_appointments(self, start_date=None, end_date=None):
        """Fetch appointments from DrChrono within date range"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
        logger.info(f"Fetching DrChrono appointments from {start_date} to {end_date}")
        
        params = {
            'date_range': f'{start_date}/{end_date}',
            'page_size': 100
        }
        
        all_appointments = []
        url = 'https://drchrono.com/api/appointments'
        
        while url:
            response = requests.get(url, headers=self.drchrono_headers, params=params)
            if response.status_code != 200:
                error_msg = f"Failed to fetch DrChrono appointments: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            data = response.json()
            all_appointments.extend(data['results'])
            url = data['next']
            params = {}  # Clear params for subsequent requests
            
        logger.info(f"Retrieved {len(all_appointments)} appointments from DrChrono")
        return all_appointments

    def get_acuity_appointments(self, start_date=None, end_date=None):
        """Fetch appointments from Acuity within date range"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
        logger.info(f"Fetching Acuity appointments from {start_date} to {end_date}")
        
        params = {
            'minDate': start_date,
            'maxDate': end_date
        }
        
        response = requests.get(
            'https://acuityscheduling.com/api/v1/appointments', 
            auth=self.acuity_auth,
            params=params
        )
        
        if response.status_code != 200:
            error_msg = f"Failed to fetch Acuity appointments: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        appointments = response.json()
        logger.info(f"Retrieved {len(appointments)} appointments from Acuity")
        return appointments

    def create_drchrono_appointment(self, appointment_data):
        """Create a new appointment in DrChrono"""
        logger.info(f"Creating new appointment in DrChrono: {appointment_data.get('appointment_type', 'Unknown type')}")
        
        response = requests.post(
            'https://drchrono.com/api/appointments',
            headers=self.drchrono_headers,
            json=appointment_data
        )
        
        if response.status_code in [201, 200]:
            logger.info(f"Successfully created appointment in DrChrono")
            return response.json()
        else:
            error_msg = f"Failed to create DrChrono appointment: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def create_acuity_appointment(self, appointment_data):
        """Create a new appointment in Acuity"""
        logger.info(f"Creating new appointment in Acuity for {appointment_data.get('firstName', '')} {appointment_data.get('lastName', '')}")
        
        response = requests.post(
            'https://acuityscheduling.com/api/v1/appointments',
            auth=self.acuity_auth,
            json=appointment_data
        )
        
        if response.status_code in [201, 200]:
            logger.info(f"Successfully created appointment in Acuity")
            return response.json()
        else:
            error_msg = f"Failed to create Acuity appointment: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def convert_acuity_to_drchrono(self, acuity_appointment):
        """Convert Acuity appointment format to DrChrono format"""
        # Extract date and time from Acuity appointment
        date_obj = datetime.fromisoformat(acuity_appointment.get('datetime').replace('Z', '+00:00'))
        
        # Calculate duration in minutes
        duration = acuity_appointment.get('duration', 60)  # Default to 60 minutes if not specified
        
        # Format schedule data for DrChrono
        drchrono_data = {
            'scheduled_time': date_obj.strftime('%Y-%m-%dT%H:%M:%S'),
            'duration': duration,
            'exam_room': acuity_appointment.get('location', ''),
            'notes': acuity_appointment.get('notes', ''),
            'reason': acuity_appointment.get('type', ''),
            # Patient details would need to be properly mapped
            # This is a simplified example - you'll need to map patient IDs or create patients
            'patient': self.find_or_create_drchrono_patient(acuity_appointment),
            'status': 'Confirmed'
        }
        
        return drchrono_data
    
    def convert_drchrono_to_acuity(self, drchrono_appointment):
        """Convert DrChrono appointment format to Acuity format"""
        # Get patient info from DrChrono
        patient_id = drchrono_appointment.get('patient')
        patient_info = self.get_drchrono_patient(patient_id)
        
        # Get appointment type ID from Acuity
        # This is a simplified example - you'll need to map appointment types
        appointment_type_id = self.get_matching_acuity_appointment_type(drchrono_appointment.get('reason', ''))
        
        # Format data for Acuity
        acuity_data = {
            'appointmentTypeID': appointment_type_id,
            'datetime': drchrono_appointment.get('scheduled_time'),
            'firstName': patient_info.get('first_name', ''),
            'lastName': patient_info.get('last_name', ''),
            'email': patient_info.get('email', ''),
            'phone': patient_info.get('phone', ''),
            'notes': drchrono_appointment.get('notes', '')
        }
        
        return acuity_data
    
    def find_or_create_drchrono_patient(self, acuity_appointment):
        """Find existing patient in DrChrono or create new one from Acuity data"""
        # This is a simplified implementation
        # In a real implementation, you would search for matching patients first
        # and only create a new one if no match is found
        
        # For demonstration purposes, we'll assume the need to create a new patient
        patient_data = {
            'first_name': acuity_appointment.get('firstName', ''),
            'last_name': acuity_appointment.get('lastName', ''),
            'email': acuity_appointment.get('email', ''),
            'home_phone': acuity_appointment.get('phone', '')
        }
        
        # In a real implementation you would:
        # 1. Search for existing patients
        # 2. Return patient ID if found
        # 3. Create new patient only if not found
        
        # This is a placeholder for demonstration
        return self.create_drchrono_patient(patient_data)
    
    def create_drchrono_patient(self, patient_data):
        """Create a new patient in DrChrono"""
        logger.info(f"Creating new patient in DrChrono: {patient_data.get('first_name')} {patient_data.get('last_name')}")
        
        response = requests.post(
            'https://drchrono.com/api/patients',
            headers=self.drchrono_headers,
            json=patient_data
        )
        
        if response.status_code in [201, 200]:
            logger.info(f"Successfully created patient in DrChrono")
            return response.json().get('id')
        else:
            error_msg = f"Failed to create DrChrono patient: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_drchrono_patient(self, patient_id):
        """Fetch patient details from DrChrono"""
        logger.info(f"Fetching patient {patient_id} from DrChrono")
        
        response = requests.get(
            f'https://drchrono.com/api/patients/{patient_id}',
            headers=self.drchrono_headers
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully retrieved patient from DrChrono")
            return response.json()
        else:
            error_msg = f"Failed to fetch DrChrono patient: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_matching_acuity_appointment_type(self, drchrono_reason):
        """Find matching appointment type in Acuity based on DrChrono reason"""
        # In a real implementation, you would:
        # 1. Fetch all appointment types from Acuity
        # 2. Match against the DrChrono reason
        # 3. Return the appropriate appointmentTypeID
        
        # This is a placeholder implementation
        response = requests.get(
            'https://acuityscheduling.com/api/v1/appointment-types',
            auth=self.acuity_auth
        )
        
        if response.status_code != 200:
            error_msg = f"Failed to fetch Acuity appointment types: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        appointment_types = response.json()
        
        # Simple matching logic - improve this based on your specific needs
        for apt_type in appointment_types:
            if drchrono_reason.lower() in apt_type.get('name', '').lower():
                return apt_type.get('id')
        
        # Return first appointment type as fallback
        if appointment_types:
            return appointment_types[0].get('id')
        else:
            raise Exception("No appointment types found in Acuity")
    
    def sync_acuity_to_drchrono(self, days=30):
        """Sync appointments from Acuity to DrChrono"""
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        logger.info(f"Starting sync from Acuity to DrChrono ({start_date} to {end_date})")
        
        # Get appointments from Acuity
        acuity_appointments = self.get_acuity_appointments(start_date, end_date)
        
        # Get existing DrChrono appointments for deduplication
        drchrono_appointments = self.get_drchrono_appointments(start_date, end_date)
        
        # Track created appointments
        created_count = 0
        
        for acuity_apt in acuity_appointments:
            # Check if appointment already exists in DrChrono
            # This is a simplified implementation - improve matching logic based on your needs
            duplicate = False
            acuity_datetime = datetime.fromisoformat(acuity_apt.get('datetime').replace('Z', '+00:00'))
            
            for drchrono_apt in drchrono_appointments:
                drchrono_datetime = datetime.fromisoformat(drchrono_apt.get('scheduled_time').replace('Z', '+00:00'))
                time_diff = abs((acuity_datetime - drchrono_datetime).total_seconds())
                
                # If appointments are within 5 minutes of each other and have same patient info
                # consider them duplicates
                if time_diff < 300 and acuity_apt.get('lastName', '').lower() in drchrono_apt.get('patient_name', '').lower():
                    duplicate = True
                    break
            
            if not duplicate:
                try:
                    # Convert and create in DrChrono
                    drchrono_data = self.convert_acuity_to_drchrono(acuity_apt)
                    self.create_drchrono_appointment(drchrono_data)
                    created_count += 1
                except Exception as e:
                    logger.error(f"Error syncing appointment {acuity_apt.get('id')}: {str(e)}")
        
        logger.info(f"Acuity to DrChrono sync complete. Created {created_count} new appointments.")
        return created_count
    
    def sync_drchrono_to_acuity(self, days=30):
        """Sync appointments from DrChrono to Acuity"""
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        logger.info(f"Starting sync from DrChrono to Acuity ({start_date} to {end_date})")
        
        # Get appointments from DrChrono
        drchrono_appointments = self.get_drchrono_appointments(start_date, end_date)
        
        # Get existing Acuity appointments for deduplication
        acuity_appointments = self.get_acuity_appointments(start_date, end_date)
        
        # Track created appointments
        created_count = 0
        
        for drchrono_apt in drchrono_appointments:
            # Check if appointment already exists in Acuity
            # This is a simplified implementation - improve matching logic based on your needs
            duplicate = False
            
            if drchrono_apt.get('scheduled_time'):
                drchrono_datetime = datetime.fromisoformat(drchrono_apt.get('scheduled_time').replace('Z', '+00:00'))
                
                for acuity_apt in acuity_appointments:
                    acuity_datetime = datetime.fromisoformat(acuity_apt.get('datetime').replace('Z', '+00:00'))
                    time_diff = abs((drchrono_datetime - acuity_datetime).total_seconds())
                    
                    # If appointments are within 5 minutes of each other and have similar details
                    # consider them duplicates
                    patient_info = self.get_drchrono_patient(drchrono_apt.get('patient'))
                    if time_diff < 300 and patient_info.get('last_name', '').lower() in acuity_apt.get('lastName', '').lower():
                        duplicate = True
                        break
                
                if not duplicate:
                    try:
                        # Convert and create in Acuity
                        acuity_data = self.convert_drchrono_to_acuity(drchrono_apt)
                        self.create_acuity_appointment(acuity_data)
                        created_count += 1
                    except Exception as e:
                        logger.error(f"Error syncing appointment {drchrono_apt.get('id')}: {str(e)}")
        
        logger.info(f"DrChrono to Acuity sync complete. Created {created_count} new appointments.")
        return created_count

    def run_bidirectional_sync(self, interval_minutes=60, days_to_sync=30):
        """Run a continuous bidirectional sync between DrChrono and Acuity"""
        logger.info(f"Starting bidirectional sync with {interval_minutes} minute interval")
        
        while True:
            try:
                # Authenticate with both systems
                self.authenticate_drchrono()
                self.authenticate_acuity()
                
                # Sync appointments in both directions
                acuity_to_drchrono = self.sync_acuity_to_drchrono(days_to_sync)
                drchrono_to_acuity = self.sync_drchrono_to_acuity(days_to_sync)
                
                logger.info(f"Sync complete. Created {acuity_to_drchrono} appointments in DrChrono and {drchrono_to_acuity} in Acuity.")
                
                # Wait for next sync interval
                logger.info(f"Waiting {interval_minutes} minutes for next sync...")
                time.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in sync process: {str(e)}")
                logger.info(f"Will retry in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)


def load_config(config_file='config.json'):
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file {config_file}")
        return None


if __name__ == '__main__':
    # Load configuration
    config = load_config()
    
    if not config:
        # Use environment variables if config file not found
        config = {
            'drchrono_api_key': os.environ.get('DRCHRONO_API_KEY'),
            'acuity_user_id': os.environ.get('ACUITY_USER_ID'),
            'acuity_api_key': os.environ.get('ACUITY_API_KEY'),
            'sync_interval': int(os.environ.get('SYNC_INTERVAL', 60)),
            'days_to_sync': int(os.environ.get('DAYS_TO_SYNC', 30))
        }
    
    # Check if required credentials are available
    if not all([config.get('drchrono_api_key'), config.get('acuity_user_id'), config.get('acuity_api_key')]):
        logger.error("Missing required API credentials. Check configuration file or environment variables.")
        exit(1)
    
    logger.info("DrChrono-Acuity Connector is starting...")
    
    # Initialize connector
    connector = DrChronoAcuityConnector(
        config.get('drchrono_api_key'),
        config.get('acuity_user_id'),
        config.get('acuity_api_key')
    )
    
    # Run bidirectional sync
    connector.run_bidirectional_sync(
        interval_minutes=config.get('sync_interval', 60),
        days_to_sync=config.get('days_to_sync', 30)
    )
