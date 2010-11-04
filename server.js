var sys = require('sys'),
    underscore = require('underscore'),
    express = require('express'),
    calc = require('./graphcalc')

var width = 500;
var height = 500;
var epsilon = 0.01;
var force_cutoff = 1;
var node_count = 10;

var Node = function(id) {
    this.id = id;
    
    this.color = Math.random();
    this.size = Math.random();
}

var init = function() {
    var nodes = [];
    for (var i = 0; i < node_count; i++) {
        nodes.push(new Node(i))
    }
    
    var edges = {};
    _.each(nodes, function(thisNode) {
        if (!edges[thisNode.id]) edges[thisNode.id] = {}
        _.each(nodes, function(otherNode) {
            if (!edges[otherNode.id]) edges[otherNode.id] = {}
            if (thisNode == otherNode) {
                edges[thisNode.id][otherNode.id] = 0;
            } else if (!edges[thisNode.id][otherNode.id]) {
                var weight = Math.abs(thisNode.color - otherNode.color);
                edges[thisNode.id][otherNode.id] = weight;
                edges[otherNode.id][thisNode.id] = weight;
            }
        })
    })
    return {nodes: nodes, edges: edges};
}

var app = express.createServer();
app.use(express.staticProvider(__dirname + '/public'));

app.get('/', function(req, res) { res.sendfile(__dirname + '/public/index.html'); })

app.get('/data', function(req, res) {
    var data = init();
    
    res.header('Content-Type', 'application/json');
    res.send(JSON.stringify(data));
})

app.listen(3000);