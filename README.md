# Roobot Takeaway API
operatie nuggies

# Run
uvicorn main:app --reload

# Build
git clone https://github.com/seleniumbase/SeleniumBase.git
cd /SeleniumBase
docker build --no-cache -t seleniumbase-local .
docker images seleniumbase-local //Check for errors

cd /RoobotFood
docker build --no-cache -t roobotfood:1.0 .

# Run
cd /RoobotFood
docker run --rm --init --shm-size=2g -p 8000:8000 --name roobotfood roobotfood:1.0

# Debug PythonAPI
cd /RoobotFood
uvicorn main:app --reload


# Config
"ideal",
"creditcard":{
    "CardNumber":"1",
    "ExpiryDate":"1",
    "SecurityCode":"1",
    "cc-name":"1"
    }

If your using discord you can post to api using discord user id and the server wil find the user information and automaticly fill it in

# me
docker run --rm --init --shm-size=2g -p 8000:8000 --name roobotfood -v "C:\Users\vandu\Documents\GitHub\Roobot-Takeaway-API\RoobotFood\config.json:/app/config.json" roobotfood:1.0

docker run --rm --init --shm-size=2g -p 8000:8000 --name roobotfood -v "C:\Users\vandu\Documents\GitHub\Roobot-Takeaway-API\RoobotFood\:/app/" roobotfood:1.0