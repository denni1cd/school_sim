"""Core configuration loading module."""
import os
import yaml

def load_configurations(config_dir: str = "configs") -> dict:
    """Load all configuration YAML files from the given directory."""
    configs = {}
    # Load population config
    pop_path = os.path.join(config_dir, "population.yaml")
    if os.path.exists(pop_path):
        with open(pop_path, 'r') as f:
            data = yaml.safe_load(f)
            configs['population'] = data if data else {}
    else:
        configs['population'] = {}

    # Load names (female and last)
    female_names_path = os.path.join(config_dir, "names_female.yaml")
    last_names_path = os.path.join(config_dir, "names_last.yaml")
    names = {}
    if os.path.exists(female_names_path):
        with open(female_names_path, 'r') as f:
            data = yaml.safe_load(f)
            names['female_first'] = data.get('female_first_names', []) if data else []
    else:
        names['female_first'] = []
    if os.path.exists(last_names_path):
        with open(last_names_path, 'r') as f:
            data = yaml.safe_load(f)
            names['last'] = data.get('last_names', []) if data else []
    else:
        names['last'] = []
    # Reserve key for male names in future
    names['male_first'] = []
    configs['names'] = names

    # Load uniforms config
    uni_path = os.path.join(config_dir, "uniforms.yaml")
    if os.path.exists(uni_path):
        with open(uni_path, 'r') as f:
            data = yaml.safe_load(f)
            configs['uniforms'] = data if data else {}
    else:
        configs['uniforms'] = {}

    # Load other placeholder configs
    for cfg_name in ["weather", "schedule", "academics", "inventory", "ui", "systems"]:
        file_path = os.path.join(config_dir, f"{cfg_name}.yaml")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                configs[cfg_name] = data if data else {}
        else:
            configs[cfg_name] = {}

    return configs
