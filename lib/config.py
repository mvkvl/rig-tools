import yaml

# reads configuration from YAML file
def read(file):
    conf = {}
    with open(file) as fp:
        conf = yaml.load(fp)
    return conf

# if given output plugin enabled
def plugin_enabled(section, plugin, conf):
    return  conf.get(section) and                      \
            conf.get(section).get(plugin) and          \
            conf.get(section).get(plugin).get("enabled")

def get_value(conf, path, default):
    b = conf
    for s in path.split("."):
        b = b.get(s)
        if b is None:
            break;
    return b
