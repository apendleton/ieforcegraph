var sys = require('sys'),
    underscore = require('underscore'),
    express = require('express'),
    calc = require('./graphcalc'),
    sqlite = require('sqlite'),
    step = require('step');

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
    var out = {}
    step(
        // make some queries
        function() {
            db.execute('select id as oid, "c" || id as id, name, party, total from candidates order by total desc limit 25', this.parallel());
            db.execute('select id as oid, "o" || id as id, name, partisanship, total from organizations order by total desc limit 25', this.parallel());
        },
        
        // do some stuff with the results
        function(error, can_rows, org_rows) {
            out.nodes = can_rows.concat(org_rows);
            
            var can_ids = _.map(can_rows, function(item) { return item.oid; });
            var org_ids = _.map(org_rows, function(item) { return item.oid; });
            db.execute('select "o" || organization_id as organization_id, "c" || candidate_id as candidate_id, weight from can_org_weights where candidate_id in (' + can_ids.join(',') + ') and organization_id in (' + org_ids.join(',') + ')', this);
        },
        
        // aggregate the edges and send a response
        function(error, edge_rows) {
            if (error) { sys.log(error); return; }
            
            var edges = {}
            _.each(edge_rows, function(edge) {
                var id1 = edge.organization_id;
                var id2 = edge.candidate_id;
                if (!edges[id1]) edges[id1] = {};
                edges[id1][id2] = parseFloat(edge.weight);
                
                if (!edges[id2]) edges[id2] = {};
                edges[id2][id1] = parseFloat(edge.weight);
            })
            
            out.edges = edges;
            
            res.header('Content-Type', 'application/json');
            res.send(JSON.stringify(out));
        }
    )
})

app.listen(3000);