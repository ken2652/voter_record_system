import requests
import os

def download_favicon():
    url = "https://th.bing.com/th/id/R.18c4d785b55537c031b3d5f2aa199e18?rik=5JRgZTuOeDm3vA&riu=http%3a%2f%2froxascity.gov.ph%2fwp-content%2fuploads%2f2021%2f08%2fcropped-HDlogo.png&ehk=aSg8X7JKQPNYVQOOvvBz2pH2H6FbP7lNULc9qPhuxZI%3d&risl=&pid=ImgRaw&r=0"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Create static directory if it doesn't exist
        os.makedirs('static', exist_ok=True)
        
        # Save the image as favicon.ico
        with open('static/favicon.ico', 'wb') as f:
            f.write(response.content)
        print("Favicon downloaded successfully!")
    else:
        print(f"Failed to download favicon. Status code: {response.status_code}")

if __name__ == "__main__":
    download_favicon() 