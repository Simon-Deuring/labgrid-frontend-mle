var express = require('express');
var app = express();

app.get('/', function (req, res) {
   res.send('Hello World');
})

var server = app.listen(4201, function () {
   var host = '127.0.0.1'
   var port = server.address().port
   
   console.log("Example app listening at http://%s:%s", host, port)
})