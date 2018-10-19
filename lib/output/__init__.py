import config
import output
import output.console
import output.influxdb

def write(conf, data, metric=None, save_function=None, module=None):
    # print result to stdout if console output is enabled in configuration
    if config.plugin_enabled("output", "console", conf):
        output.console.output(data)

    # save result to influxdb if influxdb output is enabled in configuration
    if config.plugin_enabled("output", "influxdb", conf):
        if metric and save_function:
            save_function(data,
                          conf["output"]["influxdb"],
                          metric=metric,
                          module=module)
