var sys = require('sys'),
    underscore = require('underscore'),
    express = require('express'),
    calc = require('./graphcalc'),
    sqlite = require('sqlite');

var width = 500;
var height = 500;
var epsilon = 0.01;
var force_cutoff = 1;
var node_count = 50;

var db = new sqlite.Database();
db.open(__dirname + '/data/iedata.sqlite3', function() {} );

var app = express.createServer();
app.use(express.staticProvider(__dirname + '/public'));

app.get('/', function(req, res) { res.sendfile(__dirname + '/public/index.html'); })

app.get('/data', function(req, res) {
    db.execute('select id, name, party, total from candidates order by total desc limit 25', function(error, rows) {
        var out = {}
        if (error) { sys.log(error); return; }
        out.nodes = rows;
        
        var ids = _.map(rows, function(item) { return item.id; });
        console.log('select * from can_can_weights where candidate1_id in (' + ids.join(',') + ') and candidate2_id in (' + ids.join(',') + ')')
        db.execute('select * from can_can_weights where candidate1_id in (' + ids.join(',') + ') and candidate2_id in (' + ids.join(',') + ')', function(error, rows) {
            if (error) { sys.log(error); return; }
            
            var edges = {}
            _.each(rows, function(edge) {
                var cid1 = parseInt(edge.candidate1_id);
                var cid2 = parseInt(edge.candidate2_id);
                if (!edges[cid1]) edges[cid1] = {};
                edges[cid1][cid2] = parseFloat(edge.weight);
                
                if (!edges[cid2]) edges[cid2] = {};
                edges[cid2][cid1] = parseFloat(edge.weight);
            })
            
            out.edges = edges;
            
            res.header('Content-Type', 'application/json');
            res.send(JSON.stringify(out));
        });
    })
})

app.listen(3000);