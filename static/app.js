angular.module('SketchWS',['ngAnimate','ui.bootstrap']).controller('SketchCtrl', function($scope, $http) {
    $http.get('/sketch').then(function(res) {
        $scope.sketches = Object.keys(res.data).sort().map(function(s) {
            return { name: s, ext: res.data[s], w: false }
        });
    });

    $scope.initiate_upload = function() {
        angular.element(document.querySelector('#img'))[0].click();
    };

    $scope.do_upload = function(f) {
        var formData = new FormData();
        formData.append('img', f.files[0]);
        jQuery.ajax({
           url : '/upload',
           type : 'POST',
           data : formData,
           processData: false,
           contentType: false,
           success : function(data) {
             console.log(data);
             $scope.sketches.push(data);
             var ws = new WebSocket("ws://localhost:8080/convert");
             show_progress(ws, data);
           }
        });
    };

    $scope.print = function(sketch) {
        var ws = new WebSocket("ws://localhost:8080/print");
        show_progress(ws, sketch);
    };

    function show_progress(ws, sketch) {
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
