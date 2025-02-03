from waitress import serve
import logging
import json
import ssl
from socket import socket
from wsgiref.simple_server import make_server

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Predefined response message
RESPONSE_MESSAGE = "all your bases r belong to us"

# WSGI Application that simulates a C&C server
def app(environ, start_response):
    try:
        # Read the incoming JSON payload
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        data = json.loads(post_data)
        
        # Log the received payload for debugging or monitoring
        logging.info("Received beacon with payload: %s", data)

        # Response headers
        response_headers = [
            ('Content-type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')  # Allow cross-origin requests if needed
        ]
        
        # Create the response body
        response_body = json.dumps({"message": RESPONSE_MESSAGE})

        # Return the response
        start_response('200 OK', response_headers)
        return [response_body.encode('utf-8')]

    except Exception as e:
        # If there's an error, log it and respond with an error message
        logging.error("Error processing beacon: %s", e)
        response_headers = [('Content-type', 'application/json')]
        response_body = json.dumps({"error": "Failed to process beacon"})
        start_response('400 Bad Request', response_headers)
        return [response_body.encode('utf-8')]


# Main function to start the server with HTTPS
def run_server():
    logging.info("C&C server is starting...")

    # Set up SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    # Create a raw socket to wrap it in SSL
    httpd = make_server('0.0.0.0', 443, app)
    
    # Wrap the socket with SSL context
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    # Run the server
    logging.info("Serving on https://0.0.0.0:443...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
