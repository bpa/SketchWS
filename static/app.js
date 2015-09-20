angular.module('SketchWS',['ngAnimate','ui.bootstrap']).controller('SketchCtrl', function($scope, $http) {
    $http.get('/sketch').then(function(res) {
        console.log(res);
        $scope.sketches = Object.keys(res.data).sort().map(function(s) {
            return { name: s, ext: res.data[s], w: false }
        });
        
        console.log($scope.sketches);
    });

    $scope.upload = function(sketch) {
        var ws = new WebSocket("ws://localhost:8080/upload");
    };

    $scope.print = function(sketch) {
        console.log("Printing " + sketch);
        var ws = new WebSocket("ws://localhost:8080/print");
        ws.onopen = function() {
            ws.send(sketch.name);
        };
        ws.onmessage = function(msg) {
            if (!sketch.w) {
                sketch.w = true;
                sketch.step  = 0;
                sketch.steps = parseInt(msg.data);
            }
            else {
                sketch.step++;
                sketch.label = msg.data;
            }
            $scope.$apply();
            console.log(msg.data);
        };
        ws.onclose = function() {
            console.log("printed");
            sketch.w = false;
            $scope.$apply();
        };
    };

    $scope.delete = function(sketch) {
        if (confirm("Are you sure you want to delete " + sketch.name + "?")) {
            $http.get('/sketch/' + sketch.name + '/delete');
        }
    };
});
