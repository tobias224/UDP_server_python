import socket
import threading
import json
import requests

UDP_PORT = 5000  # Updated to avoid permission issues
API_URL = "https://desksensor.azurewebsites.net/api/Desks"  # Replace with your REST server URL

# Create and bind the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))

print(f"Listening for UDP packets on all interfaces, port {UDP_PORT}...")

# Counter for assigning unique IDs
client_id = 1
client_id_lock = threading.Lock()  # To ensure thread safety

# Function to handle each client
def handle_Client(data, addr):
    global client_id
    
    try:
        # Decode the incoming message
        decoded_data = data.decode()
        
        # Parse the string data into a dictionary
        original_data = json.loads(decoded_data)
        
        # Assign a unique ID for this client
        with client_id_lock:
           unique_id = client_id
           client_id = 0

        # Transform the data into the desired JSON format
        transformed_data = {
            "id": unique_id,
            "name": original_data.get("name", "unknown"),
            "occupied": bool(original_data.get("occupied", 0))
        }
        
        # Print the transformed JSON
        print(f"Transformed data from {addr}: {json.dumps(transformed_data, indent=2)}")
        
        # Convert transformed data to JSON string
        json_string = json.dumps(transformed_data)
        
        # Send the transformed data to the REST server
        headers_array = {'Content-type': 'application/json'}
        
        
        response = requests.post(API_URL, data=json_string, headers=headers_array)
        

        # Log the response from the REST server
        print(f"REST server response: {response.status_code} - {response.text}")

    except json.JSONDecodeError:
        print(f"Failed to decode JSON from {addr}: {data.decode()}")
    except requests.RequestException as e:
        print(f"Failed to send data to REST server: {e}")

# Main loop to receive and handle data
while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes

    # Start a new thread for each client
    thread = threading.Thread(target=handle_Client, args=(data, addr))
    thread.start()

