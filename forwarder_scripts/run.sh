# Check the command line arguments
if [ "$#" -ne 1 ]; then
    echo "Run the script: ./run.sh <cs.curs_username>"
    exit 1
fi

docker run -p "5000:5000" --env USERNAME=$1 vstefanescu96/master
