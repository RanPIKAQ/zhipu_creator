from flask import Flask, render_template, request, jsonify
from time import sleep
from zhipuai import ZhipuAI
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    api_key = request.form['api_key']
    prompt = request.form['prompt']
    generation_type = request.form['generation_type']
    client = ZhipuAI(api_key=api_key)

    start_time = time.time()

    if generation_type == 'video':
        response = client.videos.generations(
            model="cogvideox",
            prompt=prompt
        )

        while True:
            response2 = client.videos.retrieve_videos_result(
                id=f"{response.id}"
            )
            if response2.task_status == "SUCCESS":
                video_data = json.loads(json.dumps(response2.to_dict()))
                video_url = video_data['video_result'][0]['url']
                elapsed_time = int(time.time() - start_time)
                return jsonify({"status": "success", "url": video_url, "type": "video", "elapsed_time": elapsed_time})
            elif response2.task_status == "FAIL":
                return jsonify({"status": "fail", "error": "Video generation failed"}), 500
            else:
                sleep(5)
    elif generation_type == 'image':
        response = client.images.generations(
            model="cogview-3",
            prompt=prompt
        )
        image_url = response.data[0].url
        elapsed_time = int(time.time() - start_time)
        return jsonify({"status": "success", "url": image_url, "type": "image", "elapsed_time": elapsed_time})
    else:
        return jsonify({"status": "fail", "error": "Invalid generation type"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')