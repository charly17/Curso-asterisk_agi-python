class WbSocket {
    constructor(uri,funAttr) {
        this.uri = uri;
        this.funAttr = funAttr;
        this.getWs()
    }
    getWs(){
        this.websocket = new WebSocket(this.uri);
        this.websocket.onopen = ()=>{
            console.log("Conectado WebS !"); 
        };
        this.websocket.onmessage = this.funAttr;
        this.websocket.onclose = (error)=>{
            console.log("Conexion Cerrrada , Estamos Reconectando !", error.reason);
            setTimeout(() => {
                this.getWs();
            }, 1000);
        };
        this.websocket.onerror = function(err) {
            console.error('Socket encountered error: ', err.message, 'Closing socket');
            if (this.websocket)
            {
                this.websocket.close();
            }
        };
    }
    send(message){
        this.websocket.send(message);
    }
    get status(){
        return this.websocket.readyState;
    }
}

// export default WbSocket;