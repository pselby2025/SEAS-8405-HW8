from flask import Flask, request, jsonify
import requests
from jose import jwt
from jose.exceptions import JWTError
from jose.backends.rsa_backend import RSAKey

app = Flask(__name__)

# Split JWKS fetch location vs. expected issuer
JWKS_URL = "http://keycloak:8080/realms/FintechApp/protocol/openid-connect/certs"
TOKEN_ISSUER = "http://localhost:8080/realms/FintechApp"
CLIENT_ID = "flask-client"

# Fetch JWKS and extract the correct RSA key by kid
def get_public_key(token):
    jwks = requests.get(JWKS_URL).json()
    headers = jwt.get_unverified_header(token)

    for key in jwks["keys"]:
        if key["kid"] == headers["kid"]:
            return RSAKey(key, algorithm="RS256")

    raise JWTError("Unable to find appropriate key")

# Decode and verify the token
def decode_token(token):
    key = get_public_key(token)
    return jwt.decode(
        token,
        key=key,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        issuer=TOKEN_ISSUER
    )

# Protected route
@app.route('/')
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]
    try:
        decoded = decode_token(token)
        return jsonify({
            "message": "Welcome!",
            "user": decoded
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401

# Health check
@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)