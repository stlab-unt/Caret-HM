import web
import json
import controllers
import os

urls = (
    '/', 'mainView',
    '/apps', 'apps',
    '/create_heatmap', 'create_heatmap'
)

cfg = { 'test_dir': '/tests',
        'image_dir': '/images',
        'number_type': 'ratio',
        'number_value': 2,
        'linkage': 'average',
        'distance_ratio': 0.1
}

class mainView:
    def GET(self):
        return json.dumps(urls)

class apps:
    def GET(self):
        web.header('Access-Control-Allow-Origin','*')
        return json.dumps(
            controllers.get_apps(cfg)
        )

class create_heatmap:
    def POST(self):
        web.header('Access-Control-Allow-Origin','*')
        data = json.loads(web.data())
        if 'number_type' in data:
            cfg['number_type'] = data['number_type'];
        if 'number_value' in data:
            cfg['number_value'] = float(data['number_value']);
        if 'linkage' in data:
            cfg['linkage'] = data['linkage'];
        if 'distance_ratio' in data:
            cfg['distance_ratio'] = float(data['distance_ratio'])

        return json.dumps(
            controllers.make_heatmaps(os.path.basename(data['app']), cfg)
        )

    def OPTIONS(self):
        web.header('Access-Control-Allow-Origin','*')
        web.header('Access-Control-Allow-Headers','Content-Type')
        return json.dumps({})

app = web.application(urls, globals())
if __name__ == "__main__":
    app.run()
application = app.wsgifunc()
