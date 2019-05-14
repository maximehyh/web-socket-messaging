# web-socket-messaging
Simple instant messaging app using flask-socketio

<img width="1680" alt="Capture d’écran 2019-04-28 à 12 34 14" src="https://user-images.githubusercontent.com/36699994/56863195-b51ab680-69b3-11e9-855b-fbc923f5a84f.png">

flask-socketio documentation: https://flask-socketio.readthedocs.io/en/latest/

Run
---
- Run 'docker-compose build' and 'docker-compose up' (need to wait a little bit for postgres container to get ready)

Tests
-----
- Run 'docker-compose run web python init_db.py' and 'docker-compose run -e TESTING=true --rm web python -m unittest'

Architecture
------------
![Architecture](https://user-images.githubusercontent.com/36699994/56863183-974d5180-69b3-11e9-8966-272e7b499f5e.png)
