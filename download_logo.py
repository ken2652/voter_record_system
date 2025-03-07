import requests
import os

def download_logo():
    url = "http://roxascity.gov.ph/wp-content/uploads/2021/08/cropped-HDlogo.png"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Create static directory if it doesn't exist
        os.makedirs('static', exist_ok=True)
        
        # Save the logo
        with open('static/logo.png', 'wb') as f:
            f.write(response.content)
        print("Logo downloaded successfully!")
    else:
        print(f"Failed to download logo. Status code: {response.status_code}")

if __name__ == "__main__":
    download_logo() 