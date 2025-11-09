import json
import time
import base64
import requests
from io import BytesIO
from PIL import Image

# https://fusionbrain.ai/en/keys/

API_KEY = "ТВОЙ КЛЮЧ"
API_SECRET = "ТВОЙ СЕКРЕТНЫЙ КЛЮЧ"
BASE_URL = "https://api-key.fusionbrain.ai/"

def get_pipeline():
    headers = {'X-Key': f'Key {API_KEY}', 'X-Secret': f'Secret {API_SECRET}'}
    r = requests.get(BASE_URL + 'key/api/v1/pipelines', headers=headers)
    return r.json()[0]['id']

def generate(prompt, pipeline):
    headers = {'X-Key': f'Key {API_KEY}', 'X-Secret': f'Secret {API_SECRET}'}
    params = {
        "type": "GENERATE",
        "numImages": 1,
        "width": 1024,
        "height": 1024,
        "generateParams": {"query": prompt}
    }
    data = {
        'pipeline_id': (None, pipeline),
        'params': (None, json.dumps(params), 'application/json')
    }
    r = requests.post(BASE_URL + 'key/api/v1/pipeline/run', headers=headers, files=data)
    return r.json()['uuid']

def check(uuid):
    headers = {'X-Key': f'Key {API_KEY}', 'X-Secret': f'Secret {API_SECRET}'}
    for _ in range(40):
        r = requests.get(BASE_URL + f'key/api/v1/pipeline/status/{uuid}', headers=headers)
        data = r.json()
        if data['status'] == 'DONE':
            return data['result']['files'][0]
        elif data['status'] == 'FAIL':
            raise Exception("Ошибка генерации.")
        time.sleep(5)
    raise TimeoutError("Превышено время ожидания.")

def show_image(b64):
    img = Image.open(BytesIO(base64.b64decode(b64)))
    img.show()
    img.save("result.png")
    print("✅ Изображение сохранено как result.png")

if __name__ == "__main__":
    pipeline = get_pipeline()
    while True:
        prompt = input("\nВведите промт: ").strip()
        if not prompt:
            continue
        print("🕓 Ждём изображение...")
        try:
            uuid = generate(prompt, pipeline)
            img_b64 = check(uuid)
            show_image(img_b64)
        except Exception as e:
            print("❌ Ошибка:", e)
        if input("\nПерегенерировать (п) или выйти (з)? ").lower().startswith("з"):
            break
