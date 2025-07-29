import requests
import json

with open("data.json", "r") as file:
    data = json.load(file)

try:
    piper_config = data.get("piper_config", {})
    ip = piper_config.get("host", "127.0.0.1")
    port = piper_config.get("port", "10200")
    end_point = piper_config.get("end_point", "/api/text-to-speech")
    voice = piper_config.get("voice", "en_US-lessac-medium") # Default voice
except KeyError as e:
    print(f"Key error: {e}. Please check your data.json file for the correct keys.")

piper_url = f"http://{ip}:{port}{end_point}?voice={voice}"

print("Piper URL:", piper_url)

def get_text(chunk_text):
    try:
        return requests.post(
            piper_url,
            data=chunk_text.encode('utf-8'),
            headers={'Content-Type': 'text/plain'}
        )
    except Exception as e:
        print("Piper request failed:", e)


# if __name__ == "__main__":

