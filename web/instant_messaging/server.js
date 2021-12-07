const port = process.env.PORT || 3000;
const io = require('socket.io')(port);
const redisAdapter = require('socket.io-redis');
io.adapter(redisAdapter({ host: 'localhost', port: 6379 }));

const users = {}

io.on('connection', socket => {
    socket.on('new-user', ({room, name}) => {
        console.log(name + ' connected to ' + room);
        users[name] = socket.id
        socket.nickname = name
        socket.join(room);
        socket.broadcast.to(room).emit('user-connected', users);
    })
    socket.on('send-chat-message', ({room, message, name}) => {
        console.log(name + ' send: ' + message);
        socket.broadcast.to(room).emit('chat-message', { message: message, name })
    })
    socket.on('whisper', ({room, message, nickname}, callback) => {
        console.log('Whisper!')
        if (nickname in users) {
            socket.to(users[nickname]).emit('whisper', {name: socket.nickname, message})
            callback(message)
        } else {
            callback('Please enter a valid username.')
        }
    })
})
