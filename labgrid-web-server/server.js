var express = require('express');
var app = express();

var places;
var resources;

var autobahn = require('autobahn');
var connection = new autobahn.Connection({
   url: "ws://127.0.0.1:8080/ws",
   realm: "realm1"
});
connection.onopen = function (session, details) {
   console.log('Connection successfully accomplished')
};
connection.onopen = function (session, details) {
   // Request places from coordinator
   session.call('org.labgrid.coordinator.get_places').then(res => places = res);
   //places = await session.call('org.labgrid.coordinator.get_places');

   // Request hardware resources from coordinator
   session.call('org.labgrid.coordinator.get_resources').then(res => resources = res);
   //resources = await session.call('org.labgrid.coordinator.get_places');
};
connection.onclose = function (reason, details) {
   // handle connection lost
}
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