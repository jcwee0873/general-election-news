import os
import re
import json
import yaml
from dotenv import load_dotenv


class ScrapConfig:
    def __init__(self, config_path=None) -> None:
        def eval_parsing(d):
            if isinstance(d, dict):
                bridge = {}
                for k, v in d.items():
                    try:
                        if v == 'quote':
                            bridge[k] = v
                            continue

                        bridge[k] = eval(v)
                    
                    except :
                        bridge[k] = v
                return bridge

            else :
                return d
            
        if not config_path:
            config_path = os.path.join(CURR_PATH, '../..', 'scrap_config.json')
            config_path = os.path.abspath(config_path)

        with open(config_path, 'r') as f:
            scrap_config = json.load(f, object_hook=eval_parsing)
         
        self.config = scrap_config
