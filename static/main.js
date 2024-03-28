const form = document.querySelector(".sendmessage");
const textarea = document.querySelector("#content");
if (form) {
    const button = document.querySelector("#msgbtn");
    button.addEventListener('click', (e) => {
        e.preventDefault();
        textAreaSend(e);
    });
    textarea.addEventListener("keyup", (e) => {
        if (e.key == 'Enter') {
            e.preventDefault();
            textAreaSend(e);
        }
    })
}

function textAreaSend(e) {
    if (textarea.value.trim() !== '') {
        sendMessage();
    }
    textarea.value = '';
}

var socket = io();

// Evento para lidar com o envio de mensagens
function sendMessage() {
    var message = document.querySelector('#content').value;
    socket.emit('sendMessage', message);
}

// Evento para lidar com a recepção de mensagens
socket.on('receiveMessage', function(data) {
    // Atualiza a interface do usuário com a nova mensagem recebida
    let messageElement = document.createElement('div');
    messageElement.classList.add("message");
    let title = document.createElement('div');
    title.classList.add("title");
    let picture = document.createElement("img");
    picture.src = data.picturePath;
    let userInfo = document.createElement('h5');
    userInfo.textContent = `${data.username} ${data.datetime}`;
    let p = document.createElement('p');
    title.appendChild(picture);
    title.appendChild(userInfo);
    messageElement.appendChild(title);
    p.textContent = data.content;
    messageElement.appendChild(p);
    document.querySelector('.messages').prepend(messageElement);
});
