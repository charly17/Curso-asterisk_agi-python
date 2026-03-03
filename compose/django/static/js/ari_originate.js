const channel = document.getElementById('channel');
const extension = document.getElementById('extension');
const context = document.getElementById('context');
const makeCall = document.getElementById('make-call');

makeCall.addEventListener('click', () => {

    const chlVal = channel.value;
    const ctxVal = context.value;
    const extVal = extension.value;

    if(chlVal != '' && extVal != ''  && ctxVal != '') {
        const response = postRequest(
            'http://localhost:8000/ari/api/post',
            {
                method: 'POST',
                uri: `http://asterisk:8088/ari/channels?endpoint=${chlVal}&extension=${extVal}&priority=1&context=${ctxVal}&callerId=${extVal}`
            }
        );
    } else {
        alert('faltan datos para realizar la acción');
    }
});


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