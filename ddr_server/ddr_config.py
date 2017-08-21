import yaml


def get_config(key):
    with open("ddr_config.props", 'r') as propsfile:
        props = yaml.load(propsfile)
    return props.get(key)