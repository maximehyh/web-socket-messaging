from main import app, socketio, message_directed
import unittest


class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/',
            data=dict(username="ffmpeg", password="rocks"),
            follow_redirects=True
        )
        self.assertIn(b'Chat Room', response.data)

    def test_login_required(self):
        tester = app.test_client(self)
        response = tester.get(
            '/chat',
            content_type='html/text',
            follow_redirects=True
        )
        self.assertIn(b'Please login', response.data)


class TestSocketIO(unittest.TestCase):

    def test_broadcast(self):
        client = socketio.test_client(app)
        client.get_received()
        client.emit('message_event', {'message': 'olala'})
        received = client.get_received()

        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'message_event_response')
        self.assertEqual(received[0]['args'][0]['message'], 'olala')

    def test_directed_message(self):
        # First we need to create username session variable
        with app.test_client() as logged_test_client:
            with logged_test_client.session_transaction() as session:
                session['username'] = 'ffmpeg'

        # Then we call a socketio test client using HTTP
        # logged test client
        client = socketio.test_client(
            app,
            flask_test_client=logged_test_client,
            namespace='/private'
        )

        # Store session username in logged_users in order to be able to 
        # get session_id = logged_users[data['username']] in private_message
        # event
        client.emit('username')

        client.emit(
            'private_message',
            {'message': 'vous salut', 'username': 'ffmpeg', 'origin': 'BigBuck'},
            callback=True,
            namespace='/private'
        )

        received = client.get_received()

        self.assertEqual(len(received), 1)
        self.assertEqual(len(received[0]['args']), 1)
        self.assertEqual(received[0]['name'], 'new_private_message')
        self.assertEqual(received[0]['args'][0], 'BigBuck : vous salut')


if __name__ == '__main__':
    unittest.main()
