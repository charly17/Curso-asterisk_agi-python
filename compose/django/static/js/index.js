const ws = new WbSocket('ws://localhost:8000/ws/', eventFunction);
const contentDiv = document.getElementById('data-response');
const callButton = document.getElementById('consulta-peer');

function eventFunction({data}){
    console.log(JSON.parse(data));
    objectResponse = JSON.parse(data);
    if (objectResponse.action == 'iax_peers') {
        contentDiv.innerText = JSON.stringify(objectResponse.event);
    }
}


callButton.addEventListener('click', ()=>{
    ws.send('IAXPeers');
})