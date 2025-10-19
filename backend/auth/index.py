'''
Business: User registration and authentication with JWT tokens
Args: event with httpMethod, body (email, password, name for registration)
Returns: HTTP response with JWT token or error message
'''

import json
import os
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt(user_id: int, email: str) -> str:
    secret = os.environ.get('JWT_SECRET', 'default-secret-key-change-in-production')
    exp = int((datetime.utcnow() + timedelta(days=7)).timestamp())
    
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip('=')
    payload = base64.urlsafe_b64encode(json.dumps({"user_id": user_id, "email": email, "exp": exp}).encode()).decode().rstrip('=')
    
    signature = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    
    return f"{header}.{payload}.{signature}"

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        secret = os.environ.get('JWT_SECRET', 'default-secret-key-change-in-production')
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header, payload, signature = parts
        
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        ).decode().rstrip('=')
        
        if signature != expected_signature:
            return None
        
        payload_data = json.loads(base64.urlsafe_b64decode(payload + '=='))
        
        if payload_data['exp'] < int(datetime.utcnow().timestamp()):
            return None
        
        return payload_data
    except Exception:
        return None

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if action == 'register':
                email = body_data.get('email')
                password = body_data.get('password')
                name = body_data.get('name')
                
                if not email or not password or not name:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Email, password and name are required'}),
                        'isBase64Encoded': False
                    }
                
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    return {
                        'statusCode': 409,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'User already exists'}),
                        'isBase64Encoded': False
                    }
                
                password_hash = hash_password(password)
                cur.execute(
                    "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s) RETURNING id, email, name",
                    (email, password_hash, name)
                )
                user = cur.fetchone()
                conn.commit()
                
                token = create_jwt(user['id'], user['email'])
                
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'token': token,
                        'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}
                    }),
                    'isBase64Encoded': False
                }
            
            elif action == 'login':
                email = body_data.get('email')
                password = body_data.get('password')
                
                if not email or not password:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Email and password are required'}),
                        'isBase64Encoded': False
                    }
                
                password_hash = hash_password(password)
                cur.execute(
                    "SELECT id, email, name FROM users WHERE email = %s AND password_hash = %s",
                    (email, password_hash)
                )
                user = cur.fetchone()
                
                if not user:
                    return {
                        'statusCode': 401,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Invalid credentials'}),
                        'isBase64Encoded': False
                    }
                
                token = create_jwt(user['id'], user['email'])
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'token': token,
                        'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}
                    }),
                    'isBase64Encoded': False
                }
            
            elif action == 'verify':
                token = body_data.get('token')
                
                if not token:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Token is required'}),
                        'isBase64Encoded': False
                    }
                
                payload = verify_jwt(token)
                
                if not payload:
                    return {
                        'statusCode': 401,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Invalid token'}),
                        'isBase64Encoded': False
                    }
                
                cur.execute("SELECT id, email, name FROM users WHERE id = %s", (payload['user_id'],))
                user = cur.fetchone()
                
                if not user:
                    return {
                        'statusCode': 401,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'User not found'}),
                        'isBase64Encoded': False
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}
                    }),
                    'isBase64Encoded': False
                }
            
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Invalid action'}),
                    'isBase64Encoded': False
                }
        
        finally:
            cur.close()
            conn.close()
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }
