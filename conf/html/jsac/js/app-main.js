angular.
    module('adminAreaMain',[]).
        component('adminAreaMain', {
            templateUrl: 'tpl/adminAreaMain.html',
            controller: function adminAreaMainController($http) {
                    scope = this;
                    scope.counter = 0;
                    scope.ntypes = [
                                        {
                                            'number_type': 'ratio',
                                            'text': "Ratio (ratio * number of observed activitivies)"
                                        },{
                                            'number_type': 'fixed',
                                            'text': "Number (a fixed number of clusters)"
                                    }];
                    scope.linkages = ['average', 'complete'];
                    scope.linkage = scope.linkages[0];
                    scope.ntype=scope.ntypes[0];
                    scope.clusters = 2;
                    scope.distance_ratio = 0.1;
                    $http.get('/hmg/apps').then(function(r) {
                        scope.apps = r.data;
                        scope.app = scope.apps[0];
                    });

                    scope.newImage = function(isrc) {
                        return isrc+'?'+scope.counter;
                    };

                    scope.submitApp = function () {
                        scope.counter++;
                        scope.loading=1;
                        scope.slides = null;
                        $http.post('/hmg/create_heatmap', JSON.stringify({
                                'app': scope.app,
                                'number_type': scope.ntype.number_type,
                                'number_value': scope.clusters,
                                'linkage': scope.linkage,
                                'distance_ratio': scope.distance_ratio
                            })).then(function(r) {
                                scope.slides = [];
                                for(var idx in r.data.images) {
                                    scope.slides.push({'image': r.data.images[idx]});
                                }
                                scope.stats = r.data.stats;
                                scope.loading=null;
                        });
                    };
                }});
