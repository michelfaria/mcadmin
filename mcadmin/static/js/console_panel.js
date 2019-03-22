// mcadmin/static/js/console_panel.js

// nodes
var consoleBox;

window.addEventListener('load', function () {
    consoleBox = document.getElementById('console-box');
    initEventSource();
});

function initEventSource() {
    var eventSource = new EventSource(MA_CONSTS.CONSOLE_PANEL_STREAM);

    eventSource.onerror = function () {
        console.error(MA_CONSTS.EVENTSOURCE_DISCONNECT_MSG);
        this.close();
    };

    eventSource.onmessage = function (msg) {
        console.log('EventSource: ' + msg.data);

        if (msg.data === MA_CONSTS.SERVER_SHUTDOWN_ERR_CODE) {
            consoleShutdown();
        } else {
            addConsoleLine(msg.data);
        }
    };
}

function consoleShutdown() {
    addConsoleLine('Server is not running');
}

function addConsoleLine(text) {
    consoleBox.value += text + '\n';
}