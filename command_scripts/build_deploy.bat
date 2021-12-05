@echo off

docker build --tag gramanicu-load-balancer .

docker create gramanicu-load-balancer