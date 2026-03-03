const user = 'astuser2'
const passwd = 'asterisk'
const uri = `ws://localhost:8088/ari/events?api_key=${user}:${passwd}&app=apptest`
const ws = new WbSocket(uri, onEvents);

let stasisObject = undefined;

keys = document.getElementsByClassName('number');
for(key of keys){
    key.addEventListener('click', ({target}) => {
        if(stasisObject != undefined) {
            stasisObject.sayDigits(target.value);
        } else {
            console.error('No hay objeto de stasis creado');
        }
    })
}

const hold = document.getElementById('hold');

hold.addEventListener('click', ({target}) => {
    const status = document.getElementById('status-hold');
    if(stasisObject != undefined) {
        if(target.value == 'unhold') {
            target.value = 'hold';
            console.log('if unhold', target.value);
            status.classList.toggle('fa-play');
            status.classList.toggle('fa-pause');
            stasisObject.hold();
        }else if(target.value == 'hold') {
            target.value = 'unhold';
            console.log('if hold', target.value);
            status.classList.toggle('fa-pause');
            status.classList.toggle('fa-play');
            stasisObject.unhold();
        }
    } else {
        target.value = 'unhold';
    }
});

const playback = document.getElementById('playback');

playback.addEventListener('click', ({target}) => {
    const status = document.getElementById('status-hold');
    stasisObject != undefined && stasisObject.playback('hello-world');
});

const redirect = document.getElementById('redirect');

redirect.addEventListener('click', ({target}) => {
    const status = document.getElementById('status-hold');
    stasisObject != undefined && stasisObject.redirect('IAX2/101');
});


// Eventos del websocket
function onEvents({data}){
    console.log(JSON.parse(data));
    const event = JSON.parse(data);
    switch(event.type) {
        case 'StasisStart':
                const display = document.getElementById('display');
                display.innerHTML = event.channel.caller.number;
                stasisObject = new StasisApp(event.channel);
                stasisObject.answer()
            break;
    }
};

// Clase para enviar acciones a Asterisk usuando http request
class StasisApp {
    constructor(channel) {
        this.channel = channel;
        this.channelId = channel.id;
        this.asteHTTP = `http://asterisk:8088/ari/`;
        this.djangoHTTP = `http://localhost:8000/ari/api/post`;
    }

    async answer() {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/answer`,
            }
        );
    };

    async sayDigits(digit) {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/play?media=sound:digits/${digit}`,
            }
        );
    };

    async playback(name) {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/play?media=sound:${name}`,
            }
        );
    };

    async hold() {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/hold`
            }
        );
    };

    async unhold() {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'DELETE',
                uri: `${this.asteHTTP}channels/${this.channelId}/hold`
            }
        );
    };

    async redirect(endpoint) {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/redirect?endpoint=${endpoint}`
            }
        )
    };
};

// HTTP request
async function postRequest(url, params = undefined, headers) {
    try {
        const urlObject = new URL(url);
        const request = {
            method: 'POST',
            body: JSON.stringify(params) || '{}',
            headers: {
                'Content-type': 'application/json;',
                ...headers
            }
        };
        const response = await fetch(urlObject, request);
        const dataResult = await response.json();
        console.log(dataResult);
        return dataResult;
    } catch (error) {
        console.error(error);
    }
};
