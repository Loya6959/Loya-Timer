let cl = document.querySelector(".main-view .left-bar #c");
let dl = document.querySelector(".main-view .left-bar #d");
let al = document.querySelector(".main-view .left-bar #a");

let cc = document.querySelector(".main-view .right-view .c");
let dc = document.querySelector(".main-view .right-view .d");
let ac = document.querySelector(".main-view .right-view .a");

let t_data = dc.querySelector(".t-data")

/**@type {HTMLFormElement} */
const config_form = document.querySelector(
    ".main-view .right-view .c #config_form")

function sw_config(display_config_name) {
    switch (display_config_name) {
        case "c":
            cl.setAttribute("data-is-select", "1");
            cc.setAttribute("data-is-select", "1");

            dl.setAttribute("data-is-select", "0");
            al.setAttribute("data-is-select", "0");

            dc.setAttribute("data-is-select", "0");
            ac.setAttribute("data-is-select", "0");
            break;
        case "d":
            dl.setAttribute("data-is-select", "1");
            dc.setAttribute("data-is-select", "1");

            cl.setAttribute("data-is-select", "0");
            al.setAttribute("data-is-select", "0");

            cc.setAttribute("data-is-select", "0");
            ac.setAttribute("data-is-select", "0");
            break;
        case "a":
            al.setAttribute("data-is-select", "1");
            ac.setAttribute("data-is-select", "1");

            cl.setAttribute("data-is-select", "0");
            dl.setAttribute("data-is-select", "0");

            cc.setAttribute("data-is-select", "0");
            dc.setAttribute("data-is-select", "0");
            break;
    }
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours.toString()
        .padStart(2, "0")}:${minutes
            .toString().padStart(2, "0")}:${remainingSeconds
                .toString().padStart(2, "0")}`;
}

async function _config_upload() {
    const _form = new FormData(config_form);

    try {
        const q = await fetch("/config/update", {
            method: "POST",
            body: _form
        });

        console.log(await q.json());
    }
    catch (e) {
        console.log("提交失败", e);
    }
}

config_form.addEventListener("submit", (event) => {
    event.preventDefault();
    _config_upload();
    location.reload();
})

async function switch_run(_state) {
    const q = await fetch(`/timer/set-state&${_state}`);
}

async function clear_timer_id() {
    const q = await fetch("/timer/clear-id");
}

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

async function get_time() {

    let q = await fetch("/timer/get-time");

    if (!q.ok) throw new Error(q.statusText);

    return await q.json();

}

async function deplete_save_time() {
    try {
        const q = await fetch("/timer/deplete-save-time");
    }
    catch {
        ;
    }
}

async function reset_base_time() {
    try {
        const q = await fetch("/timer/reset");
    }
    catch {
        ;
    }
}

async function save_config() {
    try {
        const q = fetch("/timer/save");
    }
    catch {
        ;
    }
}

async function get_t_data() {
    let is_stop = t_data.querySelector("p #is_stop");
    let is_clear = t_data.querySelector("p #is_clear");
    let save_time = t_data.querySelector("p #save_time");

    let temp1 = await is_run();
    let temp2 = await get_time();

    is_stop.textContent = temp1 ? "否" : "是";
    is_clear.textContent = (temp2.base_time > 0) ? "否" : "是";
    save_time.textContent = formatTime(temp2.save_time);
}

setInterval(get_t_data, 1000);
