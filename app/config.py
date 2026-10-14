import json
import pprint

try:
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    print("INFO:     Found config:")
    pprint.pp(config)
except Exception:
    try:
        with open("example-config.json", "r", encoding="utf-8") as f:
            example_config = json.load(f)
    except:
        raise Exception("Docker directory misconfigured. please ref to doc")
    else:
        example_config = pprint.pformat(example_config)
        raise Exception(f"There was no /app/config/config.json present! \nPlease check out the docs for more info \nExample config:\n{example_config}")