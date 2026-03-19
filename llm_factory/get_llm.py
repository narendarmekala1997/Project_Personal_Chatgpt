from llama_index.llms.ollama import Ollama
from config.settings import Settings

settings = Settings()
OLLAMA_URL = settings.OLLAMA_URL

#Module-level cache for model and instance
_current_model_name=None
_current_model_instance=None

def get_ollama_list(model_name : str):

    global _current_model_name, _current_model_instance

    if _current_model_name == model_name and _current_model_instance is not None:
        return _current_model_instance

    llm = Ollama(model=model_name, base_url=OLLAMA_URL,request_timeout=60.0,
                 client_kwargs={
                     "verify": False,
                     "trust_env": False,  # 🔥 THIS FIXES THE HANG
                 })
    _current_model_name = model_name
    _current_model_instance=llm

    return llm

#check llm usage
# check_llm = get_ollama_list(model_name="llama3:latest")
# print(check_llm)
# print(type(check_llm))
