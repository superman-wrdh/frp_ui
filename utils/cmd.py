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


if __name__ == '__main__':
    # result = cmd("ipconfig")
    result = cmd("ps -ef|grep frpc.ini")
    # result = cmd("ipconfig")
    result = result.split("\n")
    print(result)
    pss = [i for i in result if str(i).strip() and not str(i).count("grep") > 0]
    if len(pss) > 0:
        ts = [i for i in pss[0].split(" ") if i.strip()]
        pid = ts[1] if len(ts) > 1 else None
        if pid:
            kill_cmd = "kill {}".format(pid)
            print(kill_cmd)
            cmd(kill_cmd)
