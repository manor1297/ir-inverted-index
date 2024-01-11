import requests
import pickle

payload = pickle.load(open("project2_index_details.pickle", "rb"))
res = requests.post("", json=payload, timeout=600)
res = res.json()
print(res)
