import json
import time
import random
import requests
from concurrent import futures
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


executor = futures.ThreadPoolExecutor(max_workers=1)
ServerToken = "curliksienmlcld"
url = "http://127.0.0.1:8080/api/analysis-requests/write-result"


def probability_function():
    return random.random()
    
def analisys_result(modeling):
    return {
      "modelingId": modeling['modelingId'],
      "result": modeling['nodeQuantity'] * (modeling['clientmodelingQuantity'] / modeling['queueSize']) * probability_function() - 1,
    }

def get_results(req_body):
    time.sleep(5)
    results = []
    for modeling in req_body['modelings']:
        res = analisys_result(modeling)
        results.append(res)
    response = {"requestId": req_body['requestId'], "results": results}
    print(response)
    return response

def status_callback(task):
    try:
      result = task.result()
      print(result)
    except futures._base.CancelledError:
      return
    requests.put(url, data=json.dumps(result), timeout=3)

@api_view(['Put'])
def calcResults(request):
    req_body = json.loads(request.body)
    if req_body["Server-Token"] == ServerToken:
        task = executor.submit(get_results, req_body)
        task.add_done_callback(status_callback)        
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


