#! ./env/Scripts/python.exe

from atexit import register
from json import dump as json_dump
from json import load as json_load
from pathlib import Path
from time import time

from typing import Any
from typing import Literal
from typing import NoReturn
from typing import Optional

from bottle import Bottle
from bottle import FormsDict
from bottle import request
from bottle import static_file
from bottle import template
from uuid import uuid4


with open("./config.json", "r", encoding="utf-8") as js_file:
    # 读取配置文件
    cfg: dict[str, dict[str, Any]] = json_load(js_file)


ROOT_PATH: str = "./views"
ASSETS_PATH: tuple[str, ...] = ("css", "js", "img")

loya_timer_root: Bottle = Bottle()

base_time: int = cfg["user"]["base-time"]
save_time: int = cfg["save"]["save-time"]

timer_add: int = 0

synchronous_start: int = int(time())
timer_is_run: bool = True
timer_id: Optional[str] = None


def add_time() -> NoReturn:
    """
    安全的处理时间变更的函数
    Returns:
        NoReturn: 这个函数不返回任何值
    """
    global base_time, save_time, timer_add

    if timer_add >= 0:
        # 在增减池大于0时直接增加
        base_time += timer_add
    else:
        if abs(timer_add) > base_time:
            # 绝对值大于当前基准时间的情况下 消耗存档时间
            timer_add += base_time
            base_time = 0
            save_time += timer_add

            if save_time <= 0:
                save_time = 0
        else:
            base_time += timer_add

    timer_add = 0  # 清空增减池


@loya_timer_root.route("/favicon.ico")
def favicon_ico() -> Any:
    """
    一个很蠢的接口，这个接口用来解决前端favicon.ico 404 NOT FOUND的错误
    Returns:
        Any: 主要我也不知道这玩意儿到底会返回什么 也许是单纯的bytes？
    """
    return static_file("favicon.ico", ROOT_PATH)


# 程序退出时需要执行的操作


@register
def save_config() -> NoReturn:
    """
    将当前运行时配置保存到配置文件
    Returns:
        NoReturn: 这个函数只会执行操作 不会返回任何值
    """
    global cfg, save_time

    cfg["save"]["save-time"] = save_time

    if cfg["user"]["auto-save"] is True:
        cfg["save"]["save-time"] += base_time

    with open("./config.json", "w", encoding="utf-8") as js_file:
        json_dump(cfg, js_file, ensure_ascii=False, indent=4)


# 各种要用的暴露给前端的API

# file (接口数: 1)
@loya_timer_root.route("/file/<file_type>$<file_name>")
def get_file(file_type: str, file_name: str) -> Any:
    """
    请求各种资源的接口 使用$符号分割文件类型和文件名
    Args:
        file_type(str): 文件类型
        file_name(str): 文件名
    Returns:
        Any: 反正是资源 我想应该没有自定义函数用这个函数的返回值
    """

    web_get_path: Path = Path(ROOT_PATH)

    if file_type not in ASSETS_PATH:
        assert False, "尝试访问非法资源"

    result_path: Path = web_get_path / file_type / file_name

    if result_path.is_file() is True:
        return static_file(str(result_path), "./")


# timer(接口数: 7)
@loya_timer_root.route("/timer/time-synchronous$<only_flush>")
def time_synchronous(only_flush: str) -> dict[str, int]:
    """
    时间同步接口
    Returns:
        dict: 进行时间修正后的秒数
    """
    global synchronous_start, base_time, timer_is_run
    now: int = int(time())

    if only_flush != "1":  # 防止旧的实例触发计时刷新
        if timer_is_run is False:
            return {
                "base_time": base_time
            }

        add_time()
        if ((now - synchronous_start) <= base_time):
            base_time -= (now - synchronous_start)
        else:
            if cfg["user"]["auto-use-save"] is True:
                # 在自动消耗存档开启的情况下 消耗存档
                deplete_save_time()
            else:
                base_time = 0
                timer_is_run = False

    synchronous_start = now  # 记录当前的时间戳作为下一次时间同步的开始时间

    return {
        "base_time": base_time
    }


@loya_timer_root.route("/timer/get-time")
def get_time() -> dict[str, int]:
    """
    返回计时器时间
    Returns:
        dict: 在前端会变成一段JSON
    """
    return {
        "base_time": base_time,
        "save_time": save_time
    }


@loya_timer_root.route("/timer/set-state&<_start>")
def set_state(_start: Literal["0", "1"]) -> dict[
        Literal["ok"], Literal["yes", "no"]]:
    """
    设置是否开始
    Returns:
        dict: 告诉前端状态的字典
    """
    global timer_is_run
    match _start:
        case "0": timer_is_run = True
        case "1": timer_is_run = False
        case _never:
            assert False, "前端给了个意外的值 真是让人无语"

    return {"ok": "yes"}


@loya_timer_root.route("/timer/is-run")
def is_run() -> dict[str, bool]:
    """
    向前端返回计时状态
    Returns:
        dict: 返回一个说明状态的字典 前端拿到的数据是JSON
    """
    return {
        "is_run": timer_is_run
    }


@loya_timer_root.route("/timer/clear-id")
def clear_timer_id() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    清空所有实例
    Returns:
        dict: 一个告诉前端操作状态的字典
    """
    global timer_id
    timer_id = None

    return {
        "ok", "yes"
    }


@loya_timer_root.route("/timer/global-id", method="POST")
def global_id() -> dict[str, bool]:
    """
    向前端返回当前的唯一计时器ID
    Returns:
        dict: 一个告诉前端数据的JSON
    """
    web_self_id: FormsDict = request.forms

    if web_self_id.get("sid") == timer_id:
        return {
            "is_eq": True
        }
    else:
        return {
            "is_eq": False
        }


@loya_timer_root.route("/timer/deplete-save-time")
def deplete_save_time() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    手动消耗存档时间 并且将其添加到计时
    Returns:
        dict: 告诉状态的JSON
    """
    global save_time, base_time
    if save_time > 0:
        if save_time >= cfg["user"]["auto-save-deplete"]:
            save_time -= cfg["user"]["auto-save-deplete"]
            base_time += cfg["user"]["auto-save-deplete"]
        else:
            base_time += save_time
            save_time = 0
    else:
        save_time = 0

    return {
        "ok": "yes"
    }


@loya_timer_root.route("/timer/reset")
def reset() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    重置基本时间
    Returns:
        dict: 告诉状态的JSON
    """
    global base_time

    base_time = cfg["user"]["base-time"]

    return {
        "ok": "yes"
    }


@loya_timer_root.route("/timer/save")
def web_save_config() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    手动保存存档 这个操作会直接清空当前基准时间剩余 并将其划入存档 同时会立刻停止计时
    Returns:
        dict: 告诉状态的JSON
    """
    global save_time, base_time, timer_is_run

    save_time += base_time
    base_time = 0
    timer_is_run = False

    save_config()

    return {
        "ok": "yes"
    }


# config (接口数: 2)
@loya_timer_root.route("/config/update", method="POST")
def config_update() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    更新现有的配置（会立刻覆盖本地配置文件）
    Returns:
        dict: 一个表示状态的字典 前端则会拿到JSON
    """
    global cfg, base_time

    from_web_cfg: FormsDict = request.forms
    update_key: tuple[str, ...] = ("theme-color", "live-room", "base-time",
                                   "auto-save-deplete", "auto-flush-time")

    for k in update_key:
        if k in ("base-time", "auto-save-deplete", "auto-flush-time"):
            cfg["user"][k] = int(from_web_cfg.get(k))
        else:
            cfg["user"][k] = from_web_cfg.get(k)

    cfg["user"]["auto-save"] = True if from_web_cfg.get(
        "auto-save") == "True" else False
    cfg["user"]["auto-use-save"] = True if from_web_cfg.get(
        "auto-use-save") == "True" else False

    base_time = int(from_web_cfg.get("base-time"))

    with open("./config.json", "w", encoding="utf-8") as js_file:
        json_dump(cfg, js_file, ensure_ascii=False, indent=4)

    return {
        "ok": "yes"
    }


@loya_timer_root.route("/config/get-trigger")
def get_trigger() -> dict[str, list[dict[str, Any]]]:
    """
    返回包装触发器列表的字典(JSON)
    Returns:
        dict: 触发器列表
    """
    return {"data": cfg["save"]["gifts"]}


# trigger (接口数: 3)
@loya_timer_root.route("/trigger/add-trigger", method="POST")
def add_trigger() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    添加触发器 返回一个告诉是否成功的字典
    Returns:
        dict: 告诉状态的字典
    """
    trigger_temp: FormsDict = request.forms
    temp_dict: dict[str, Any] = {
        "name": None,
        "add": 0
    }

    print(trigger_temp)

    temp_dict["name"] = trigger_temp.get("name")
    temp_dict["add"] = int(trigger_temp.get("add"))

    cfg["save"]["gifts"].append(temp_dict)

    save_config()

    return {
        "ok": "yes"
    }


@loya_timer_root.route("/trigger/add", method="POST")
def trigger_add() -> dict[Literal["ok"], Literal["yes", "no"]]:
    """
    将触发器做出的时间修改添加到增减池
    Returns:
        dict: 告诉操作状态的JSON
    """
    global timer_add
    trigger_add_form: FormsDict = request.forms

    timer_add += int(trigger_add_form.get("add"))

    return {
        "ok": "yes"
    }


@loya_timer_root.route("/trigger/del", method="POST")
def trigger_del() -> dict[Literal["ok"], Literal["yes", "no"]]:
    global cfg

    trigger_del_form: FormsDict = request.forms
    try:
        cfg["save"]["gifts"].pop(int(trigger_del_form.get("index")))

        return {
            "ok": "yes"
        }
    except IndexError:
        return {
            "ok": "no"
        }


# 两个主要视图

@loya_timer_root.route("/timer")
def timer_view() -> Any:
    """计时器"""
    global timer_id, synchronous_start
    tid = str(uuid4())

    # if timer_id is None:
    timer_id = tid
    synchronous_start = int(time())

    return template("timer.html", self_id=tid)


@loya_timer_root.route("/")
def index_view() -> Any:
    """主页面 同时也是配置页面"""
    return template("index.html", tcolor=cfg["user"]["theme-color"],
                    cfg=cfg,
                    timer_link="127.0.0.1:"+str(cfg["loya"]["port"])+"/timer")
