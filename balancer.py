from datetime import datetime
import sys
import requests
import matplotlib.pyplot as plt
import numpy as np
import asyncio
import aiohttp

FU_URL = 'http://host.docker.internal:5000'

lowest_region = "asia"
lowest_worker = "1"
lowest_latency = 520

test_mode = 0

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


def plotTestResults(results):
    fix, ax = plt.subplots()
    req_count = [250, 375, 500]

    values = list(results.values())
    keys = list(results.keys())

    ax.plot(req_count, values[0], label=keys[0])
    ax.plot(req_count, values[1], label=keys[1])
    ax.plot(req_count, values[2], label=keys[2])
    ax.plot(req_count, values[3], label=keys[3])
    ax.plot(req_count, values[4], label=keys[4])

    ax.legend(loc='upper left')
    ax.set_title('Time taken to send the requests using different algorithms')
    ax.set_xlabel('Request count')
    ax.set_ylabel('Time (ms)')

    plt.show()


def printf(string):
    if test_mode == 0:
        print(string)


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
    printf("Waking up workers")

    for region in _workers:
        for worker in _workers[region]:
            url = computeURL(region, worker["id"])

            response = requests.get(url)
            if response.status_code != 200:
                printf("Error waking up the " +
                       region + worker["id" + "worker"])
                exit(1)
            else:
                printf(region + worker["id"] + " is up")


def updateLatencies():
    for region in _workers:
        for worker in _workers[region]:
            url = computeURL(region, worker["id"])

            response = requests.get(url)
            worker["latency"] = response.json()["response_time"]


def computeLowestWorker():
    # Computes the worker with the lowest latency, based on the
    # current workers data
    global lowest_latency, lowest_region, lowest_worker
    for region in _workers:
        for worker in _workers[region]:
            if worker["latency"] < lowest_latency:
                lowest_worker = worker["id"]
                lowest_region = region
                lowest_latency = worker["latency"]


def computeWeights():
    # Computes what "weight" should each worker have for the "algorithmSmart"
    # function. See documentation for more information

    highest_latency = 0
    for region in _workers:
        for worker in _workers[region]:
            if worker["latency"] > highest_latency:
                highest_latency = worker["latency"]

    for region in _workers:
        for worker in _workers[region]:
            worker["weight"] = highest_latency / worker["latency"]
            worker["remaining"] = worker["weight"]
            worker["sent"] = 0


def algorithmRandom(requests_number):
    # Sends all the request randomly
    url = computeURL()
    return [sendRequest(url) for _ in range(requests_number)]


def algorithmLowest(requests_number):
    # Send all request to the lowest latency worker
    computeLowestWorker()
    printf("Lowest latency worker is " + lowest_region + lowest_worker)

    url = computeURL(lowest_region, lowest_worker)
    return [sendRequest(url) for _ in range(requests_number)]

    return null


def algorithmEqualWorkers(requests_number):
    # Send request to all workers equally
    reqs = []

    i = 0
    while i < requests_number:
        for region in _workers:
            for worker in _workers[region]:
                if i < requests_number:
                    url = computeURL(region, worker["id"])
                    reqs += [sendRequest(url)]
                    i = i + 1
                else:
                    return reqs

    return reqs


def algorithmEqualRegions(requests_number):
    # Send request to all regions equally, but to random workers in that region
    reqs = []

    i = 0
    while i < requests_number:
        for region in _workers:
            if i < requests_number:
                url = computeURL(region)
                reqs += [sendRequest(url)]
                i = i + 1
            else:
                return reqs

    return reqs


def algorithmSmart(requests_number):
    # Splits the requests between the workers, based on their latency
    computeWeights()
    reqs = []

    i = 0
    while i < requests_number:
        for region in _workers:
            for worker in _workers[region]:
                if i < requests_number:
                    while worker["remaining"] >= 1:
                        url = computeURL(region, worker["id"])
                        reqs += [sendRequest(url)]
                        worker["remaining"] -= 1.0
                        worker["sent"] += 1
                        i += 1

                    worker["remaining"] += worker["weight"]
                else:
                    return reqs

    return reqs


def pickAlgorithm(requests_number, algorithm):
    # Picks a load balancing algorithm based on the number of
    # incoming requests

    if algorithm == 0:
        printf("Load balancing algorithm: Send to random workers")
        return algorithmRandom(requests_number)
    elif algorithm == 1:
        printf("Load balancing algorithm: Send to the worker with the lowest latency")
        return algorithmLowest(requests_number)
    elif algorithm == 2:
        printf("Load balancing algorithm: Send to all workers equally")
        return algorithmEqualWorkers(requests_number)
    elif algorithm == 3:
        printf("Load balancing algorithm: Send to all regions equally, but to random workers in that region")
        return algorithmEqualRegions(requests_number)
    elif algorithm == 4:
        printf(
            "Load balancing algorithm: Send to all workers, based on their relative speed")
        return algorithmSmart(requests_number)


def load_balance(requests_number, algorithm):
    # Check that all the workers are up before running the forwarder
    wakeWorkers()

    # Update latencies of each worker
    updateLatencies()

    # Execute the requests using an event loop (asynchronous operations)
    loop = asyncio.get_event_loop()

    # Prepare the list with the async requests before measuring the performance
    req_arr = pickAlgorithm(requests_number, algorithm)

    # Start counting the time when the load balancer
    # starts sending the requests and receiving the responses
    start_time = datetime.now()

    loop.run_until_complete(asyncio.gather(*req_arr))

    # Measure the execution time
    end_time = datetime.now()
    millis = round((end_time - start_time).total_seconds() * 1000)

    printf("Elapsed time for all requests: " + str(millis) + "ms")

    return millis


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Test mode
        test_mode = 1
        results = {"Random": [], "Lowest": [],
                   "Equal Workers": [], "Equal Regions": [], "Smart": []}
        i = 0
        for alg in results:
            results[alg] += [load_balance(250, i)]
            results[alg] += [load_balance(375, i)]
            results[alg] += [load_balance(500, i)]
            i += 1

        # results = {'Random': [8469, 12670, 17596], 'Lowest': [7983, 12348, 18792], 'Equal Workers': [
        #     8578, 11698, 16722], 'Equal Regions': [7795, 12595, 17194], 'Smart': [8220, 11725, 18624]}

        plotTestResults(results)
    else:
        # A specific configuration
        requests_number = int(sys.argv[1])

        algorithm = 4
        if len(sys.argv) == 3:
            algorithm = int(sys.argv[2])

        load_balance(requests_number, algorithm)
