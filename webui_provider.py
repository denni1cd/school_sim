import requests
import yaml
import os

class WebUIProvider:
    def __init__(self, config_path: str = None):
        cfg_file = config_path or os.path.join(os.path.dirname(__file__), "configs", "config.yaml")
        with open(cfg_file, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.endpoint = cfg.get("webui_api")

    def complete(self, prompt: str, max_tokens: int = 256, stop: list = None) -> str:
        payload = {"prompt": prompt, "max_tokens": max_tokens, "stop": stop or []}
        res = requests.post(self.endpoint, json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("choices", [{}])[0].get("text", "").strip()
