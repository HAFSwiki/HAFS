from .tool.func import *

def api_func_llm():
    if flask.request.method == 'POST':
        other_set = {}
        other_set["prompt"] = flask.request.form.get('prompt', '')
        other_set["ip"] = ip_check()
        other_set = json.dumps(other_set)

        if platform.system() == 'Linux':
            if platform.machine() in ["AMD64", "x86_64"]:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.amd64.bin"), sys._getframe().f_code.co_name, other_set], stdout = subprocess.PIPE).communicate()[0]
            else:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.arm64.bin"), sys._getframe().f_code.co_name, other_set], stdout = subprocess.PIPE).communicate()[0]
        else:
            if platform.machine() in ["AMD64", "x86_64"]:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.amd64.exe"), sys._getframe().f_code.co_name, other_set], stdout = subprocess.PIPE).communicate()[0]
            else:
                data = subprocess.Popen([os.path.join(".", "route_go", "bin", "main.arm64.exe"), sys._getframe().f_code.co_name, other_set], stdout = subprocess.PIPE).communicate()[0]

        data = data.decode('utf8')

        return flask.Response(response = data, status = 200, mimetype = 'application/json')
    else:
        return flask.jsonify({})