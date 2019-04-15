var isServerOn,
    serverSwitchBtn,
    serverStatusSpan,
    uptimeSpan,
    peakActivitySpan,
    serverVersionSpan;

/**
 * @param seconds
 * @constructor
 * @extends EventEmitter
 */
function Uptime(seconds) {
    this.seconds = seconds;
}

Uptime.prototype = Object.create(EventEmitter.prototype);

Uptime.prototype.constructor = Uptime;

Uptime.prototype.setSeconds = function (seconds) {
    this.seconds = seconds;
    this.emitEvent('change');
};

/**
 * @type Uptime
 */
var uptime = new Uptime(-1);


(function () {
    serverSwitchBtn = document.getElementById('server-switch');
    serverStatusSpan = document.getElementById('server-status');
    uptimeSpan = document.getElementById('uptime');
    peakActivitySpan = document.getElementById('peak-activity');
    serverVersionSpan = document.getElementById('server-version');
    initEventSource();
    initServerSwitchBtnListener();
    initUptimeCounter();
})();

function initEventSource() {
    var eventSource = new EventSource(MA_CONSTS.STATUS_PANEL_STREAM);

    eventSource.onerror = function () {
        console.error(MA_CONSTS.EVENTSOURCE_DISCONNECT_MSG);
        this.close();
    };

    eventSource.onmessage = function (msg) {
        var data = JSON.parse(msg.data);
        var isServerRunning = data['is_server_running'];
        var peakActivity = data['peak_activity'];
        var serverVersion = data['server_version'];

        uptime.setSeconds(data['uptime']);

        if (isServerRunning) {
            serverSwitchBtn.innerText = 'Turn OFF';
            serverStatusSpan.innerText = 'ON';
        } else {
            serverSwitchBtn.innerText = 'Turn ON';
            serverStatusSpan.innerText = 'OFF';
        }

        if (serverVersion) {
            serverVersionSpan.innerText = serverVersion;
        } else {
            serverVersionSpan.innerText = NOT_APPLICABLE;
        }

        isServerOn = isServerRunning;
        peakActivitySpan.innerText = peakActivity;
    }
}

function initServerSwitchBtnListener() {
    serverSwitchBtn.addEventListener('click', function () {
        var xhr = new XMLHttpRequest();
        var url = window.location;
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                console.log('XHR Status: ' + xhr.status);
                console.log('XHR Response Text: ' + xhr.responseText);
            }
        };

        var data = JSON.stringify({
            'action': isServerOn ? 'turn_off' : 'turn_on'
        });

        console.log('Sending data: ' + data);
        xhr.send(data);
    });
}

function initUptimeCounter() {
    var seconds = 0;

    uptime.addListener('change', function () {
        /**
         * @this Uptime
         */
        seconds = this.seconds;
    });

    setInterval(function () {
        if (seconds > -1) {
            seconds += 1;
            var days = Math.floor(seconds / (3600 * 24));
            var hours = Math.floor(seconds % (3600 * 24) / 3600);
            var minutes = Math.floor(seconds % 3600 / 60);
            var seconds_ = Math.floor(seconds % 60);
            uptimeSpan.innerText = pad(days, 2) + ':' + pad(hours, 2) + ':'
                + pad(minutes, 2) + ':' + pad(seconds_, 2);
        } else {
            uptimeSpan.innerText = NOT_APPLICABLE;
        }
    }, 1000);
}

function pad(num, size) {
    var s = "000000000" + num;
    return s.substr(s.length - size);
}