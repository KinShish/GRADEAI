from flask import Flask
from flask import request
from flask import abort
from flask_cors import CORS
import function.getDataCity as gtc
from threading import Thread


def create_app():
    print("Сервер запущен")
    app = Flask(__name__)
    CORS(app)

    @app.route('/api/get/city', methods=['POST'])
    def get_city():
        if not request.json or not 'name' in request.json:
            abort(400)
        try:
            return gtc.get_data_city(request.json['name'])
        except Exception as ex:
            print("Ошибка /api/get/city:", ex)
            abort(400)

    @app.route('/api/get/point', methods=['POST'])
    def get_point():
        if not request.json or not 'points' in request.json:
            abort(400)
        try:
            return gtc.get_data_point(request.json['points'], 5000)
        except Exception as ex:
            print("Ошибка /api/get/point:", ex)
            abort(400)

    @app.route('/api/get/points', methods=['POST'])
    def get_points():
        print(request.json)
        if not request.json or not 'points' in request.json or not 'dist' in request.json:
            abort(400)
        try:
            result = []
            array_thread = []
            for i in request.json['points']:
                result.append([])

            for idx, point in enumerate(request.json['points']):
                #gtc.get_data_points(point, request.json['dist'], result, idx)
                t = Thread(target=gtc.get_data_points, args=(point, request.json['dist'], result, idx))
                t.daemon = True
                t.start()
                array_thread.append(t)
            for t in array_thread:
                t.join()
                print("Завершен")
            return result
        except Exception as ex:
            print("Ошибка /api/get/point:", ex)
            abort(400)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='192.168.0.107', port=3000, debug=True)
