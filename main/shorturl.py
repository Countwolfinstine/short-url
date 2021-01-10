import os
import pymongo
from flask import Flask, redirect, request
from hashlib import md5
from waitress import serve


app = Flask("url_shortener")

mapping = {}
url_db = None

@app.route("/shorten", methods=["POST"])
def shorten():
    global mapping, url_db    
    payload = request.json    
    
    if "url" not in payload:
        return "Missing URL Parameter", 400
    
    find_in_mongo = url_db['mappings'].find_one({"url": payload["url"]})
    
    if find_in_mongo != None:
        mapping[find_in_mongo['short']] = payload["url"]
        return f"Already exists: r/{find_in_mongo['short']}\n"
    
    else:
        hash_ = md5()
        hash_.update(payload["url"].encode())
        digest = hash_.hexdigest()[:5]  
        mapping[digest] = payload["url"] # Store in local data base
        insert_result = url_db['mappings'].insert_one({"url" : payload["url"], "short" : digest} ) #Store in mongo
        
        print("insert_result", insert_result)
        
        return f"Shortened: r/{digest}\n"

@app.route("/r/<hash_>")
def redirect_(hash_):

    if hash_ in mapping:
        return redirect(mapping[hash_])
    else:
        find_in_mongo = url_db['mappings'].find_one({"short": hash_})
        if find_in_mongo != None:
            url = find_in_mongo["url"]
            mapping[hash_] = url
            return redirect(url)
        else:
            return "URL Not Found", 404


if __name__ == "__main__":
    mongo_connection_string = os.environ['MONGO_URL']
    # "mongodb://localhost:27017/"
    mongo_client = pymongo.MongoClient(mongo_connection_string)
    url_db = mongo_client["url_db"]
    
    # app.run(debug=True) For Development ENV
    serve(app, host='0.0.0.0', port=8000)

