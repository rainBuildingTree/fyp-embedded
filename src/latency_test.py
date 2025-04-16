import requests
import time

start_time = time.time()
response = requests.post(f"http://143.89.94.254:5000/upload_sign_video?api_key=1234", data='Laid back camping')
end_time = time.time()
print (start_time - end_time)
print(response.text)