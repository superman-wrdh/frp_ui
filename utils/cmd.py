from subprocess import PIPE, Popen
import chardet


def _cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]


def cmd(command):
    r = _cmdline(command)
    try:
        predict = chardet.detect(r)
        encoding = predict['encoding']
        # print(encoding)
        cr = r.decode(encoding)
    except Exception as e:
        # print(e)
        cr = "execute [{}]error"
    return cr


def get_run_info():
    import re
    result = cmd("ps -ef|grep frpc.ini")
    result = result.split("\n")
    data = {
        "info": None,
        "pid": None,
        "is_run": False
    }
    pss = [i for i in result if str(i).strip() and not str(i).count("grep") > 0]
    if len(pss) > 0:
        ts = re.split(" +", pss[0].strip())
        pid = ts[1] if len(ts) > 1 else None
        data.update({
            "info": pss[0].strip(),
            "pid": pid,
            "is_run": True
        })
    return data


def kill_process(pid):
    cmd("kill -9 {}".format(pid))


if __name__ == '__main__':
    d = get_run_info()
    pass
