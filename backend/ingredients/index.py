'''
Business: CRUD operations for ingredients (create, read, delete)
Args: event with httpMethod, body, queryStringParameters, headers (X-Auth-Token)
Returns: HTTP response with ingredient data or error message
'''

import json
import os
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import hmac
import base64
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

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

def get_user_from_token(headers: Dict[str, str]) -> Optional[int]:
    token = headers.get('X-Auth-Token') or headers.get('x-auth-token')
    if not token:
        return None
    
    payload = verify_jwt(token)
    return payload['user_id'] if payload else None

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if method == 'GET':
            params = event.get('queryStringParameters') or {}
            category = params.get('category')
            search = params.get('search')
            
            query = "SELECT id, name, unit, calories_per_100g, created_at FROM ingredients WHERE 1=1"
            params_list = []
            
            if search:
                query += " AND name ILIKE %s"
                params_list.append(f"%{search}%")
            
            query += " ORDER BY name ASC"
            
            cur.execute(query, params_list)
            ingredients = cur.fetchall()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps([dict(i) for i in ingredients], default=str),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            user_id = get_user_from_token(headers)
            
            if not user_id:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Authentication required'}),
                    'isBase64Encoded': False
                }
            
            body_data = json.loads(event.get('body', '{}'))
            
            if 'name' not in body_data:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Ingredient name is required'}),
                    'isBase64Encoded': False
                }
            
            try:
                cur.execute("""
                    INSERT INTO ingredients (name, unit, calories_per_100g)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, unit, calories_per_100g, created_at
                """, (body_data['name'], body_data.get('unit', 'г'), body_data.get('calories_per_100g')))
                
                ingredient = cur.fetchone()
                conn.commit()
                
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps(dict(ingredient), default=str),
                    'isBase64Encoded': False
                }
            
            except psycopg2.IntegrityError:
                conn.rollback()
                return {
                    'statusCode': 409,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Ingredient already exists'}),
                    'isBase64Encoded': False
                }
        
        elif method == 'DELETE':
            user_id = get_user_from_token(headers)
            
            if not user_id:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Authentication required'}),
                    'isBase64Encoded': False
                }
            
            params = event.get('queryStringParameters') or {}
            ingredient_id = params.get('id')
            
            if not ingredient_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Ingredient ID is required'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("SELECT id FROM ingredients WHERE id = %s", (ingredient_id,))
            if not cur.fetchone():
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Ingredient not found'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("DELETE FROM recipe_ingredients WHERE ingredient_id = %s", (ingredient_id,))
            cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Ingredient deleted successfully'}),
                'isBase64Encoded': False
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Method not allowed'}),
                'isBase64Encoded': False
            }
    
    finally:
        cur.close()
        conn.close()