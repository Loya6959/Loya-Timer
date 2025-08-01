/**基本时间
 * @type {number}
 */
let base_time = 0;
/**存档时间
 * @type {number}
 */
let save_time = 0;

let base_time_display = document.querySelector(
    ".timer-body .time-display #timer-time");

let base_display = document.querySelector(
    ".timer-body .time-display");

let save_time_display = document.querySelector(
    ".timer-body .save-time #save-time"
);

/**计数器 一旦到达阈值触发时间同步
 * @type {number}
 */
let count_time = 0;


/**
 * 格式化时间
 * @param {number} seconds - 总秒数
 * @returns {string} - %HH:%MM:%SS 格式的时间字符串
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours.toString()
        .padStart(2, "0")}:${minutes
            .toString().padStart(2, "0")}:${remainingSeconds
                .toString().padStart(2, "0")}`;
}


/**
 * 设置计时器上的时间显示
 * @param {number} bt - 基本时间
 * @param {number} st - 存档时间
 * @returns {void} - 只操作 不返回
 */
function set_time(bt, st) {
    base_time_display.textContent = formatTime(bt);
    save_time_display.textContent = formatTime(st);
}


/**
 * 获取时间
 * @returns {void} - 只操作 不返回
 */
async function get_time() {

    let q = await fetch("/timer/get-time");

    if (!q.ok) throw new Error(q.statusText);

    let { base_time: bt, save_time: st } = await q.json();

    base_time = bt;
    save_time = st;

    set_time(base_time, save_time);

}


/**从后端拉取时间
 * @returns {number} - 后端返回的时间 单位是秒
 */
async function time_synchronous(only_flush = "0") {
    const q = await fetch(`/timer/time-synchronous$${only_flush}`);
    if (!q.ok) throw new Error(q.statusText);

    let { base_time: bt } = await q.json();

    return bt;
}


/**
 * 获取是否开始/暂停计时
 * @returns {boolean} - 返回是否计时的布尔值
 */
async function is_run() {
    let result = false;

    try {
        let q = await fetch("/timer/is-run");
        if (!q.ok) if (!q.ok) throw new Error(q.statusText);

        temp = await q.json();
        result = temp.is_run;

        return result;
    }
    catch {
        ;
    }
}


/**
 * 获取计时器id是否与服务器相同
 */
async function is_eq_id() {
    try {
        let f = new FormData();

        f.append("sid", base_display.getAttribute("data-timer-id"));

        const q = await fetch("/timer/global-id", {
            method: "Post",
            body: f
        });

        if (!q.ok) if (!q.ok) throw new Error(q.statusText);

        temp = await q.json();
        result = temp.is_eq;
        console.log(result)

        return result;
    }
    catch {
        ;
    }
}


/**
 * 刷新时间显示
 * @returns {void} - 只操作 不返回
 */
async function flush_time() {
    
    let is_eq = await is_eq_id();

    if (!is_eq) {
        base_time_display.textContent = "已经存在一个计时器页面实例";
        base_time_display.style.fontSize = "1.8em";
        base_display.setAttribute("data-isclear", "1");
        time_synchronous("1");
        return;
    }
    
    let _run = await is_run();
    let t = await time_synchronous();

    if (!_run) {
        return;
    }

    base_time_display.textContent = formatTime(t);

    if (t > 0) {
        base_display.setAttribute("data-isclear", "0");
    }
    else {
        base_display.setAttribute("data-isclear", "1");
    }
}


get_time();
setInterval(flush_time, 1000);
setInterval(async () => {
    let q = await fetch("/timer/get-time");

    if (!q.ok) throw new Error(q.statusText);

    let { save_time: st } = await q.json();

    save_time = st;

    save_time_display.textContent = formatTime(save_time);
}, 5000)
