/**
 * @type {HTMLElement}
 */
let trigger = dc.querySelector(".add_timer");

/**
 * @type {Array}
 */
let trigger_time = [];

/**
 * @type {HTMLFormElement}
 */
const trigger_form = document.querySelector(
    ".main-view .right-view .d #timer_add");

async function add_trigger() {
    const _form = new FormData(trigger_form);

    try {
        const q = await fetch("/trigger/add-trigger", {
            body: _form,
            method: "POST"
        });
    }
    catch {
        ;
    }
}

async function get_trigger() {
    let q = await fetch("/config/get-trigger");

    if (!q.ok) throw new Error(q.statusText);

    return await q.json();
}

async function trigger_add(add_time) {
    const _form = new FormData();
    _form.append("add", add_time);

    try {
        const q = await fetch("/trigger/add", {
            body: _form,
            method: "POST"
        });
    }
    catch {
        ;
    }
}

async function trigger_del(trigger_index) {
    const _form = new FormData();
    _form.append("index", trigger_index);

    try {
        const q = await fetch("/trigger/del", {
            body: _form,
            method: "POST"
        });
    }
    catch {
        ;
    }

    flush_trigger();
}

async function flush_trigger() {
    let temp = await get_trigger();
    let trigger_list = "";

    for (let i = 0; i < temp["data"].length; i += 1) {
        trigger_time.push({
            index: i,
            add: temp["data"][i].add,
            name: temp["data"][i].name
        });

        trigger_list += `<div id="trigger">
            <span>触发器：<span>${trigger_time[i].name}</span></span>
            <span>增减值：<span>${trigger_time[i].add}</span></span>
            <button onclick="trigger_add(${trigger_time[i].add})">触发</button>
            <button onclick="trigger_del(${trigger_time[i].index})">删除该触发器</button>
            </div>`
    }

    trigger.innerHTML = trigger_list;
}

trigger_form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await add_trigger();
    await flush_trigger();
    trigger_form.reset();
})

flush_trigger();
