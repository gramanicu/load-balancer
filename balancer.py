from datetime import datetime
import sys
import requests

import asyncio
import aiohttp

FU_URL = 'http://host.docker.internal:5000'

_workers = {
    "asia": [
        {
            "id": "0",
            "latency": 520
        },
        {
            "id": "1",
            "latency": 515
        }
    ],
    "emea": [
        {
            "id": "0",
            "latency": 305
        },
    ],
    "us": [
        {
            "id": "0",
            "latency": 350
        },
        {
            "id": "1",
            "latency": 330
        },
    ]
}


def computeURL(region=None, worker=None):
    # Computes the url based on the worker region and id (if they are not provided,
    # a random worker will be used)
    if region == None:
        return FU_URL + "/work"
    elif worker == None:
        return FU_URL + "/work/" + region
    else:
        return FU_URL + "/work/" + region + "/" + worker


async def sendRequest(url):
    # Sends a request (asynchronously) to the specified url
    async with aiohttp.ClientSession() as req:
        async with req.get(url) as res:
            return await res.json()


def wakeWorkers():
    # Makes sure all the workers are up
    print("Waking up workers")

    for region in _workers:
        for worker in _workers[region]:
            url = computeURL(region, worker["id"])

            response = requests.get(url)
            if response.status_code != 200:
                print("Error waking up the " +
                      region + worker["id" + "worker"])
                exit(1)
            else:
                worker["latency"] = response.json()["response_time"]
                print(region + worker["id"] + " is up")


def algorithmRandom(request_number):
    # Sends all the request randomly
    url = computeURL()
    return [sendRequest(url) for _ in range(request_number)]


def algorithmLowest(request_number):
    # Send all request to the lowest latency worker
    return null


def algorithmEqualWorkers(request_number):
    # Send request to all workers equally
    return null


def algorithmEqualRegions(request_number):
    # Send request to all regions equally, but to random workers in that region
    return null


def algorithmSmart(request_number):
    # Splits the requests between the workers, based on their latency
    return null


def pickAlgorithm(request_number, algorithm):
    # Picks a load balancing algorithm based on the number of
    # incoming requests

    if algorithm == 0:
        print("Load balancing algorithm: Send to random workers")
        return algorithmRandom(request_number)
    elif algorithm == 1:
        print("Load balancing algorithm: Send to the worker with the lowest latency")
        return algorithmRandom(request_number)
    elif algorithm == 2:
        print("Load balancing algorithm: Send to all workers equally")
        return algorithmRandom(request_number)
    elif algorithm == 3:
        print("Load balancing algorithm: Send to all regions equally, but to random workers in that region")
        return algorithmRandom(request_number)
    elif algorithm == 4:
        print(
            "Load balancing algorithm: Send to all workers, based on their relative speed")
        return algorithmRandom(request_number)


if __name__ == "__main__":
    # Check that all the workers are up before running the forwarder
    wakeWorkers()
    request_number = int(sys.argv[1])
    algorithm = 4

    if len(sys.argv) == 3:
        algorithm = int(sys.argv[2])

    # Execute the requests using an event loop (asynchronous operations)
    loop = asyncio.get_event_loop()

    # Prepare the list with the async requests before measuring the performance
    req_arr = pickAlgorithm(request_number, 0)

    # Start counting the time when the load balancer
    # starts sending the requests and receiving the responses
    start_time = datetime.now()

    loop.run_until_complete(asyncio.gather(*req_arr))

    # Measure the execution time
    end_time = datetime.now()
    millis = round((end_time - start_time).total_seconds() * 1000)

    print("Elapsed time for all requests: " + str(millis) + "ms")
