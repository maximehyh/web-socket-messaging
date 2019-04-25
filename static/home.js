var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    socket.emit('message_event', {
        message: 'New member connected'
    })
    var form = $('form').on('submit', function(e) {
        e.preventDefault()
        let user_input = $('input.message').val()
        socket.emit('message_event', {
            message: user_input
        })
        $('input.message').val('').focus()
    })
})
socket.on('message_event_response', function(msg) {
    console.log(msg)
    if (typeof msg.message !== 'undefined') {
        $('div.message_holder').append('<div>' + msg.message + '</div>')
    }
})