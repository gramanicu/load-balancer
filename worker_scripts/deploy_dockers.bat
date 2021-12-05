@echo off & setlocal enableextensions enabledelayedexpansion

rem Check the command line arguments
if "%~1"=="" (
    ECHO Run the script^: deploy_docker.bat ^<cs.curs_username^>
    GOTO :eof
)

Rem Extract the username and change it to accommodate the Heroku constraints
set USERNAME=%1
set USERNAME=%USERNAME:.=%
set USERNAME=%USERNAME:_=%
set USERNAME=%USERNAME:@=%
set USERNAME=%USERNAME:~0,15%

Rem Convert the username to lowercase
call :ToLower %USERNAME%
set USERNAME=%ToLower%

set WORKER1=worker-asia-0
set WORKER2=worker-asia-1
set WORKER3=worker-emea-0
set WORKER4=worker-us-0
set WORKER5=worker-us-1

set APP1=%USERNAME%-%WORKER1%
set APP2=%USERNAME%-%WORKER2%
set APP3=%USERNAME%-%WORKER3%
set APP4=%USERNAME%-%WORKER4%
set APP5=%USERNAME%-%WORKER5%

Rem Create the Heroku apps
call heroku create --region eu %APP1%
call heroku create --region eu %APP2%
call heroku create --region eu %APP3%
call heroku create --region eu %APP4%
call heroku create --region eu %APP5%

set TAG1=registry.heroku.com/%APP1%/web
set TAG2=registry.heroku.com/%APP2%/web
set TAG3=registry.heroku.com/%APP3%/web
set TAG4=registry.heroku.com/%APP4%/web
set TAG5=registry.heroku.com/%APP5%/web

Rem Make sure there is no old image on the system
call docker image prune -af

Rem Pull the workers from the Docker Hub
call docker pull vstefanescu96/%WORKER1%
call docker pull vstefanescu96/%WORKER2%
call docker pull vstefanescu96/%WORKER3%
call docker pull vstefanescu96/%WORKER4%
call docker pull vstefanescu96/%WORKER5%

Rem Tag the images to accommodate the Heroku convention
call docker tag vstefanescu96/%WORKER1% %TAG1%
call docker tag vstefanescu96/%WORKER2% %TAG2%
call docker tag vstefanescu96/%WORKER3% %TAG3%
call docker tag vstefanescu96/%WORKER4% %TAG4%
call docker tag vstefanescu96/%WORKER5% %TAG5%

Rem Push the images to Heroku Registry
call docker push %TAG1%
call docker push %TAG2%
call docker push %TAG3%
call docker push %TAG4%
call docker push %TAG5%

Rem Deploy the images
call heroku container:release web --app=%APP1%
call heroku container:release web --app=%APP2%
call heroku container:release web --app=%APP3%
call heroku container:release web --app=%APP4%
call heroku container:release web --app=%APP5%

Rem Remove the local images
call docker image prune -af

:ToLower String (by val)
set ToLower=%1
for %%A in (a b c d e f g h i j k l m n o p q r s t u v w x y z
) do set ToLower=!ToLower:%%A=%%A!
goto :eof
