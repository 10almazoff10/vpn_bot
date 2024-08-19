import concurrent.futures
import requests
import time

url = "http://127.0.0.1:5000/conf/962fd229312b115fe5fb7b6d0b343a58"
num_requests = 1000  # or whatever number you want to test

start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(requests.get, url) for _ in range(num_requests)]
    results = [future.result() for future in futures]

for i, result in enumerate(results):
    response_time = (time.time() - start_time) / num_requests
    if result.status_code == 200:  # or whatever success status code you expect
        print(f"Request {i+1} successful ({response_time:.2f} seconds per request)")
    else:
        print(f"Request {i+1} failed with status code {result.status_code}")

print(f"Total requests sent in {(time.time() - start_time):.2f} seconds")