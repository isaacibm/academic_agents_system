# watsonx_llm.py
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


class WatsonXConfig:
    def __init__(self):
        self.apikey = os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY")
        self.base_url = os.getenv("WATSONX_API_BASE") or os.getenv("WATSONX_URL")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.llm_model = os.getenv("WATSONX_MODEL_ID", "watsonx/meta-llama/llama-3-1-70b-instruct")
        self.temperature = float(os.getenv("TEMPERATURE", 0))
        self.top_p = float(os.getenv("TOP_P", 1))
        self.max_tokens = int(os.getenv("MAX_TOKENS", 1024))
        self.seed = int(os.getenv("SEED", 0))
        self.embed_model = os.getenv("WATSONX_EMBEDDER_MODEL_ID", "ibm/granite-embedding-278m-multilingual")

    def build_llm(self) -> LLM:
        return LLM(
            model=self.llm_model,
            api_key=self.apikey,
            project_id=self.project_id,
            api_base=self.base_url,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            seed=self.seed,
        )

    def build_embedder_config(self) -> dict:
        # NOTE: O provider para embedding do watsonx no CrewAI (segundo issues) é "watson"
        return {
            "provider": "watson",
            "config": {
                "model": self.embed_model,
                "api_url": self.base_url,
                "api_key": self.apikey,
                "project_id": self.project_id,
            },
        }


# Singleton de fácil import
_watsonx_cfg = WatsonXConfig()


def get_llm() -> LLM:
    return _watsonx_cfg.build_llm()


def get_embedder() -> dict:
    return _watsonx_cfg.build_embedder_config()
