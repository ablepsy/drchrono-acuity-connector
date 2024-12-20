import requests

# Function to authenticate with DrChrono API
def authenticate_drchrono(api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get('https://drchrono.com/api/users/current', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to authenticate with DrChrono')

# Function to authenticate with Acuity API
def authenticate_acuity(user_id, api_key):
    response = requests.get(f'https://acuityscheduling.com/api/v1/users/{user_id}', auth=(user_id, api_key))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to authenticate with Acuity')

if __name__ == '__main__':
    print('DrChrono-Acuity Connector is running')
    # Example usage
    # drchrono_user = authenticate_drchrono('your_drchrono_api_key')
    # acuity_user = authenticate_acuity('your_acuity_user_id', 'your_acuity_api_key')
