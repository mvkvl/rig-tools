import config
import output
import redis
import output.console
import output.influxdb
import output.redis

def writeRedis(conf, data):
    output.redis.writeData(conf["output"]["redis"], data)

def write(conf, data, module="", loglevel="ERROR", metric=None, save_function=None):
    # print result to stdout if console output is enabled in configuration
    if config.plugin_enabled("output", "console", conf):
        output.console.output(data)

    # save result to influxdb if influxdb output is enabled in configuration
    if config.plugin_enabled("output", "influxdb", conf):
        if metric and save_function:
            method = getattr(output.influxdb, save_function)
            if method:
                method(data=data,
                              conf=conf["output"]["influxdb"],
                              metric=metric,
                              module=module,
                              loglevel=loglevel)

    # save result to redis if redis output is enabled in configuration
    if config.plugin_enabled("output", "redis", conf):
        if metric and save_function:
            method = getattr(output.redis, save_function)
            if method:
                method(data=data,
                              conf=conf["output"]["redis"],
                              metric=metric,
                              module=module,
                              loglevel=loglevel)
            else:
                print("METHOD NOT FOUND")
        else:
            print("WRITE IGNORED")
