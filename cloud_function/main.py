import os
import json

from google.cloud import logging
import functions_framework
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

PROJECT_ID = "{project_id}"
LOCATION = "{northamerica-northeast1}" # based on selected regions

client = logging.Client(project=PROJECT_ID)
client.setup_logging()

LOG_NAME = "run_inference-cloudfunction-log"
logger = client.logger(LOG_NAME)

@functions_framework.http
def run_inference(request):
    request_json = request.get_json(silent=True)

    if request_json and "prompt" in request_json:
        prompt = request_json["prompt"]
        logger.log(f"Received request for prompt: {prompt}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-pro")

        responses = model.generate_content(
            contents=prompt,
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.4,
                "top_p": 1,
                "top_k": 32
            },
        stream=True,
        )

        response_list = []
        for response in responses:
            try:
                response_list.append(response.text)
            except IndexError:
                response_list.append("")
                continue
        prompt_response = " ".join(response_list)
    else:
        prompt_response = "No prompt provided."

    return json.dumps({"response_text": prompt_response})