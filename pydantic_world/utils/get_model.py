import os
from typing import Union

MODELS = {
    "MISTRAL": {
        "FAST": {
            "creative": "mistral:labs-mistral-small-creative",
            "action": "mistral:mistral-small-latest"
        }
    }
}

provider = os.getenv("MODEL_PROVIDER", "MISTRAL")
model_level = os.getenv("MODEL_LEVEL", "FAST")

def get_model(type: Union["creative", "action"]):
    return MODELS[provider][model_level][type]