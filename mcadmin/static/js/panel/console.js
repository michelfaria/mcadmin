// mcadmin/static/js/console_panel.js

var consoleBox;
var consoleInput;

(function () {
    consoleBox = document.getElementById('console-box');
    consoleInput = document.getElementById('console-input');
    initEventSource();
    initConsoleInput();
})();

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

function initConsoleInput() {
    consoleInput.addEventListener('keypress', function (event) {
        if (!event) event = window.event;
        var keycode = event.which;
        if (keycode === 13) {
            // Enter key pressed
            var xhr = new XMLHttpRequest();
            var url = window.location;
            xhr.open('POST', url, true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    console.log('XHR Response status: ' + xhr.status);
                    console.log('XHR Response text: ' + xhr.responseText);
                }
            };

            xhr.send(JSON.stringify({'input_line': consoleInput.value}));
            consoleInput.value = '';
            return false;
        }
    });
}