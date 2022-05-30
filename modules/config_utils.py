from json import load, dump

def get_config(file_name: str) -> dict:
    with open(file_name, "r") as f:
        config: dict = load(f)
    return config

def overwrite_config(file_name: str,  cfg:dict):
    try:
        with open(file_name, 'w') as f:
            dump(cfg, f)
    except Exception:
        with open(f"{file_name} - error", 'w') as f:
            dump(cfg, f)