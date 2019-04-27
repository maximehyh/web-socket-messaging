// Socket for broadcast messages
var socket = io.connect('http://' + document.domain + ':' + location.port);
//Socket for private messages
var private_socket = io('http://' + document.domain + ':' + location.port + '/private');

var username = $('#username').text();

socket.on('connect', function() {
    // Displaying new user connected
    socket.emit('message_event', {
        message: username + ' connected'
    });
    // Linking username to server's session ID
    socket.emit('username');

    var form = $('form').on('submit', function(e) {
        e.preventDefault();
        // The message to be sent to through the socket
        let user_input = $('input.message').val();
        // Recipient of the message (all or specific user)
        recipient = $('#recipient').val();
        // Case : broadcast
        if (recipient == 'All') {
            socket.emit('message_event', {
                message: username + ' : ' + user_input
            });
            // Case : targeted messaging
        } else {
            private_socket.emit('private_message', {
                message: user_input,
                username: recipient,
                origin: username
            });
        };
        $('input.message').val('').focus();
    });
});

// When socket receives a 'message_event_response' event -> display message 
socket.on('message_event_response', function(msg) {
    console.log(msg)
    if (typeof msg.message !== 'undefined') {
        $('div.message_holder').append('<div>' + msg.message + '</div>')
    }
});

// Targeted  messages are shown in a pop up window
socket.on('new_private_message', function(msg) {
    alert(msg);
});


// In order to clear visible messages (not clearing DB)
$("#clearButton").click(function() {
    $("div.message_holder").empty();
});

//  Disconnecting socket and redirecting to loggin page
$('#disconnect').click(function() {
    socket.emit('disconnect_request');
    window.location.replace('http://' + document.domain + ':' + location.port);
});