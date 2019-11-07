import json
import requests as rq


def create_index(index_name):
    r = rq.put("http://localhost:9200/" + index_name)
    try:
        flag = r.json()["acknowledged"]
    except KeyError as e:
        return False
    return flag


def check_index():
    r = rq.get("http://localhost:9200/_cat/indices?v")
    return r.text


def create_content(index_name, data):
    header = {
        "Content-Type": "application/json"
    }

    r = rq.post("http://localhost:9200/" + index_name + "/_doc", data=json.dumps(data), headers=header)
    return r.json()


def search(index_name, keyword):
    r = rq.get("http://localhost:9200/" + index_name + "/_search?q=" + keyword)
    print(r.text)


if __name__ == "__main__":
    print(create_content("articles", '再随便写点好不阿红'))