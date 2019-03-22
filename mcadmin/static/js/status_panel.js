// mcadmin/static/js/status_panel.js

var serverSwitchBtn, serverStatusSpan, uptimeSpan, peakActivitySpan, serverVersionSpan;

window.addEventListener('load', function () {
    serverSwitchBtn = document.getElementById('server-switch');
    serverStatusSpan = document.getElementById('server-status');
    uptimeSpan = document.getElementById('uptime');
    peakActivitySpan = document.getElementById('peak-activity');
    serverVersionSpan = document.getElementById('server-version');
    initEventSource();
});

function initEventSource() {
    var eventSource = new EventSource(MA_CONSTS.STATUS_PANEL_STREAM);

    eventSource.onerror = function () {
        console.error(MA_CONSTS.EVENTSOURCE_DISCONNECT_MSG);
        this.close();
    };

    eventSource.onmessage = function (msg) {
        var data = JSON.parse(msg.data);

        console.log(JSON.stringify(data)); // TODO: Remove this

        var isServerRunning = data['is_server_running'];
        var uptime = data['uptime'];
        var peakActivity = data['peak_activity'];

        if (isServerRunning) {
            serverSwitchBtn.innerText = 'Turn OFF';
            serverStatusSpan.innerText = 'ON';
        } else {
            serverSwitchBtn.innerText = 'Turn ON';
            serverStatusSpan.innerText = 'OFF';
        }

        uptimeSpan.innerText = uptime;
        peakActivitySpan.innerText = peakActivity;
    }
}

// https://stackoverflow.com/questions/9763441/milliseconds-to-time-in-javascript
function msToTime(s) {

    // Pad to 2 or 3 digits, default is 2
    function pad(n, z) {
        z = z || 2;
        return ('00' + n).slice(-z);
    }

    var ms = s % 1000;
    s = (s - ms) / 1000;
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;

    return pad(hrs) + ':' + pad(mins) + ':' + pad(secs) + '.' + pad(ms, 3);
}