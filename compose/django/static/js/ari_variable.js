const user = 'astuser2'
const passwd = 'asterisk'
const uri = `ws://localhost:8088/ari/events?api_key=${user}:${passwd}&app=variables`
const ws = new WbSocket(uri, onEvents);
let stasisObject = undefined

const varLabel = document.getElementById('variable-label');
const varValue = document.getElementById('variable-value');


const setVar = document.getElementById('set-variable');
setVar.addEventListener('click', () => {
    if (stasisObject != undefined) {
        stasisObject.setVariable(varLabel.value, varValue.value);
        varLabel.value = '';
        varValue.value = '';
    } 
});

const varLabel2 = document.getElementById('variable2-label');
const getVar = document.getElementById('get-variable');
const showResult = document.getElementById('get-result');
getVar.addEventListener('click', async () => {
    if (stasisObject != undefined) {
        const response = await stasisObject.getVariable(varLabel2.value);
        varLabel.value = '';
        showResult.innerText = JSON.stringify(response);
    } 
});

const continueDial = document.getElementById('continue-dial');
continueDial.addEventListener('click', () => {
    if (stasisObject != undefined) {
        const response = stasisObject.continue();
    } 
});


// Eventos del websocket
function onEvents({data}){
    const event = JSON.parse(data);
    console.log(event);
    switch(event.type) {
        case 'StasisStart':
                stasisObject = new StasisApp(event.channel);
            break;
        case 'ChannelDtmfReceived':
                switch(event.digit) {
                    case 1:

                        break;
                }
            break;
    };
};

// Clase para enviar acciones a Asterisk usuando http request
class StasisApp {
    constructor(channel) {
        this.channel = channel;
        this.channelId = channel.id;
        this.asteHTTP = `http://asterisk:8088/ari/`;
        this.djangoHTTP = `http://localhost:8000/ari/api/post`;
    }

    async setVariable(variable, value) {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/variable?variable=${variable}&value=${value}`,
            }
        );
    };

    async getVariable(variable) {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'GET',
                uri: `${this.asteHTTP}channels/${this.channelId}/variable?variable=${variable}`,
            }
        );
        return response;
    };

    async continue() {
        const response = await postRequest(
            this.djangoHTTP,
            {
                method: 'POST',
                uri: `${this.asteHTTP}channels/${this.channelId}/continue`,
            }
        );
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