var express = require('express');
var app = express();

var autobahn = require('autobahn');
var connection = new autobahn.Connection({
   url: "ws://127.0.0.1:8080/ws",
   realm: "realm1"
});
connection.onopen = function (session, details) {
   console.log('Connection successfully accomplished')
};
connection.open();

// REST methods
app.get('/', function (req, res) {
   res.send('Hello World');
})

var server = app.listen(4201, function () {
   var host = '127.0.0.1'
   var port = server.address().port
   
   console.log("Example app listening at http://%s:%s", host, port)
})