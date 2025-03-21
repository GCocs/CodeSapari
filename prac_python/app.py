from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

# 아래 uri를 복사해둔 uri로 수정하기
uri = "mongodb+srv://ysh062100:<db_password>@cluster0.etvh1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, 27017)  # MongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle


#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################



#####
# 아래의 각각의 @app.route 은 RESTful API 하나에 대응됩니다.
# @app.route() 의 첫번째 인자는 API 경로,
# 생략 가능한 두번째 인자는 해당 경로에 적용 가능한 HTTP method 목록을 의미합니다.

# API #1: HTML 틀(template) 전달
@app.route('/')
def home():
    return render_template('111.html')


# API #2: 휴지통에 버려지지 않은 영화 목록을 반환합니다.
@app.route('/api/list', methods=['GET'])
def show_movies():
    #client에서 요청한 정렬 방식을 확인합니다. 없다면 기본적으로 좋아요 순으로 정렬합니다.
    sortMode = request.args.get('sortMode', 'likes')

    # 1. db에서 trashed가 False인 movie 목록을 검색합니다.
    # 주어진 정렬 방식으로 정렬합니다.
    if sortMode == 'likes':
        movies = list(db.movies.find({'trashed': False}, {}).sort('likes', -1))
    elif sortMode == 'running-time':
        movies = list(db.movies.find({'trashed': False}, {}).sort('running_time', -1))
    elif sortMode == 'released-year':
        movies = list(db.movies.find({'trashed': False}, {}).sort('released_year', -1))
    else:
        return jsonify({'result': 'failure'})

    # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
    return jsonify({'result': 'success', 'movies_list': movies})

# API #3: 영화에 좋아요 숫자를 하나 올립니다.
@app.route('/api/like', methods=['POST'])
def like_movie():
    # 1. client 요청에서 id를 전달받습니다.
    m_id = request.form['id']
    # 2. movies 목록에서 find_one으로 id가 매칭되는 영화 하나를 찾습니다.
    #    _id에서 string으로 그냥 찾으면 몽고DB가 검색에 실패하므로, ObjectId로 바꿔줍니다.
    movie = db.movies.find_one({'_id': ObjectId(m_id)})
    # 3. movie의 like 에 1을 더해준 new_like 변수를 만듭니다.
    new_likes = movie['likes'] + 1

    # 4. movies 목록에서 id 가 매칭되는 영화의 like 를 new_like로 변경합니다.
    result = db.movies.update_one({'_id': ObjectId(m_id)}, {'$set': {'likes': new_likes}})

    # 5. 하나의 영화만 영향을 받아야 하므로 result.updated_count 가 1이면  result = success 를 보냅니다.
    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #4: 휴지통에 버려진 영화 목록을 반환합니다.
@app.route('/api/list/trash', methods=['GET'])
def show_trash_movies():
    
    # /api/list와 구조가 비슷합니다.
    sortMode = request.args.get('sortMode', 'likes')

    # 1. db에서 trashed가 True인 movie 목록을 검색합니다.
    # 위와 마찬가지로 주어진 정렬 방식으로 정렬합니다.
    if sortMode == 'likes':
        movies = list(db.movies.find({'trashed': True}, {}).sort('likes', -1))
    elif sortMode == 'running-time':
        movies = list(db.movies.find({'trashed': True}, {}).sort('running_time', -1))
    elif sortMode == 'released-year':
        movies = list(db.movies.find({'trashed': True}, {}).sort('released_year', -1))
    else:
        return jsonify({'result': 'failure'})

    # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
    return jsonify({'result': 'success', 'movies_list': movies})


# API #5: 영화를 휴지통으로 보냅니다.
@app.route('/api/trash/go', methods=['POST'])
def goto_trash():
    # 1. cliet 요청에서 id를 전달받습니다.
    m_id = request.form['id']
    # 2. movies 목록에서 id가 매칭되는 영화의 trashed를 True로 변경합니다.
    result = db.movies.update_one({'_id': ObjectId(m_id)}, {'$set': {'trashed': True}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #6: 영화를 휴지통에서 꺼내옵니다.
@app.route('/api/trash/restore', methods=['POST'])
def restore_trash():
    # /api/trash/go 와 구조가 비슷합니다.
    m_id = request.form['id']
    # trashed값을 False로 변경합니다.
    result = db.movies.update_one({'_id': ObjectId(m_id)}, {'$set': {'trashed': False}})

    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

# API #7: 영화를 영구적으로 삭제합니다.
@app.route('/api/trash/delete', methods=['POST'])
def delete_trash():
    m_id = request.form['id']
    # id를 기준으로 movie를 찾아 삭제합니다.
    result = db.movies.delete_one({'_id': ObjectId(m_id)})

    # 삭제 체크는 modified_count가 아닌 deleted_count로 할 수 있습니다.
    if result.deleted_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)