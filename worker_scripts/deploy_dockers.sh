# Check the command line arguments
if [ "$#" -ne 1 ]; then
    echo "Run the script: ./deploy_docker.sh <cs.curs_username>"
    exit 1
fi

# Extract the username and change it to accommodate the Heroku constraints
USERNAME=$1
USERNAME="${USERNAME//[^0-9a-zA-Z]/}"
USERNAME="$(echo $USERNAME | head -c 15 | tr '[:upper:]' '[:lower:]')"

WORKER1="worker-asia-0"
WORKER2="worker-asia-1"
WORKER3="worker-emea-0"
WORKER4="worker-us-0"
WORKER5="worker-us-1"

APP1="$USERNAME-$WORKER1"
APP2="$USERNAME-$WORKER2"
APP3="$USERNAME-$WORKER3"
APP4="$USERNAME-$WORKER4"
APP5="$USERNAME-$WORKER5"

# Create the Heroku apps
heroku create --region eu $APP1
heroku create --region eu $APP2
heroku create --region eu $APP3
heroku create --region eu $APP4
heroku create --region eu $APP5

TAG1="registry.heroku.com/$APP1/web"
TAG2="registry.heroku.com/$APP2/web"
TAG3="registry.heroku.com/$APP3/web"
TAG4="registry.heroku.com/$APP4/web"
TAG5="registry.heroku.com/$APP5/web"

# Make sure there is no old image on the system
docker image prune -af 2> /dev/null

# Pull the workers from the Docker Hub
docker pull "vstefanescu96/$WORKER1"
docker pull "vstefanescu96/$WORKER2"
docker pull "vstefanescu96/$WORKER3"
docker pull "vstefanescu96/$WORKER4"
docker pull "vstefanescu96/$WORKER5"

# Tag the images to accommodate the Heroku convention
docker tag "vstefanescu96/$WORKER1" $TAG1
docker tag "vstefanescu96/$WORKER2" $TAG2
docker tag "vstefanescu96/$WORKER3" $TAG3
docker tag "vstefanescu96/$WORKER4" $TAG4
docker tag "vstefanescu96/$WORKER5" $TAG5

# Push the images to Heroku Registry
docker push $TAG1
docker push $TAG2
docker push $TAG3
docker push $TAG4
docker push $TAG5

# Deploy the images
heroku container:release web --app=$APP1
heroku container:release web --app=$APP2
heroku container:release web --app=$APP3
heroku container:release web --app=$APP4
heroku container:release web --app=$APP5

# Remove the local images
docker image prune -af 2> /dev/null
