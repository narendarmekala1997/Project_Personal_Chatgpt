from config.settings import Settings

settings = Settings()

def get_ollama_models_list():
    models_list = settings.OLLAMA_MODELS
    ollama_models = [model.strip() for model in models_list.split(',') if model.strip()]
    return ollama_models
#Example Usage
# check_models = get_ollama_models_list()
# print(type(check_models))
# print(check_models)
