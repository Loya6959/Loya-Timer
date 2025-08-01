#! ./env/Scripts/python.exe

from web import loya_timer_root
from web import cfg

if __name__ == "__main__":
    try:
        loya_timer_root.run(host="127.0.0.1",
                            port=cfg["loya"]["port"],
                            reloader=cfg["loya"]["reload"],
                            debug=cfg["loya"]["debug"])
    except KeyboardInterrupt:
        # 这个软件暂时不会提供别的退出方式
        pass