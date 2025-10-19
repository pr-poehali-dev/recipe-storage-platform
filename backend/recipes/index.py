'''
Business: CRUD operations for recipes (create, read, update, delete)
Args: event with httpMethod, body, queryStringParameters, headers (X-Auth-Token)
Returns: HTTP response with recipe data or error message
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
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
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
            recipe_id = params.get('id')
            category = params.get('category')
            search = params.get('search')
            user_id = get_user_from_token(headers)
            
            if recipe_id:
                if user_id:
                    cur.execute("""
                        SELECT r.id, r.user_id, r.title, r.description, r.image_url,
                               r.cooking_time, r.servings, r.difficulty, r.category_id,
                               r.instructions, r.created_at, r.updated_at,
                               u.name as author_name
                        FROM recipes r
                        LEFT JOIN users u ON r.user_id = u.id
                        WHERE r.id = %s AND (true OR r.user_id = %s)
                    """, (recipe_id, user_id))
                else:
                    cur.execute("""
                        SELECT r.id, r.user_id, r.title, r.description, r.image_url,
                               r.cooking_time, r.servings, r.difficulty, r.category_id,
                               r.instructions, r.created_at, r.updated_at,
                               u.name as author_name
                        FROM recipes r
                        LEFT JOIN users u ON r.user_id = u.id
                        WHERE r.id = %s
                    """, (recipe_id,))
                recipe = cur.fetchone()
                
                if not recipe:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Recipe not found'}),
                        'isBase64Encoded': False
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps(dict(recipe), default=str),
                    'isBase64Encoded': False
                }
            
            else:
                query = """
                    SELECT r.id, r.user_id, r.title, r.description, r.image_url,
                           r.cooking_time, r.servings, r.difficulty, r.category_id,
                           r.instructions, r.created_at, r.updated_at,
                           u.name as author_name
                    FROM recipes r
                    LEFT JOIN users u ON r.user_id = u.id
                    WHERE 1=1
                """
                params_list = []
                
                if user_id:
                    query += " AND (true OR r.user_id = %s)"
                    params_list.append(user_id)
                
                if category:
                    query += " AND r.category_id = %s"
                    params_list.append(category)
                
                if search:
                    query += " AND (r.title ILIKE %s OR r.description ILIKE %s)"
                    search_pattern = f"%{search}%"
                    params_list.extend([search_pattern, search_pattern])
                
                query += " ORDER BY r.created_at DESC"
                
                cur.execute(query, params_list)
                recipes = cur.fetchall()
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps([dict(r) for r in recipes], default=str),
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
            
            required_fields = ['title', 'cooking_time', 'servings', 'difficulty', 'instructions']
            for field in required_fields:
                if field not in body_data:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': f'Missing required field: {field}'}),
                        'isBase64Encoded': False
                    }
            
            cur.execute("""
                INSERT INTO recipes (user_id, title, description, image_url, cooking_time, servings, difficulty, category_id, instructions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, title, description, image_url, cooking_time, servings, difficulty, category_id, instructions, created_at, updated_at
            """, (
                user_id,
                body_data['title'],
                body_data.get('description', ''),
                body_data.get('image_url', ''),
                body_data['cooking_time'],
                body_data['servings'],
                body_data['difficulty'],
                body_data.get('category_id'),
                body_data['instructions']
            ))
            
            recipe = cur.fetchone()
            recipe_id = recipe['id']
            
            ingredients = body_data.get('ingredients', [])
            for ing in ingredients:
                cur.execute("""
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (recipe_id, ingredient_id) DO UPDATE
                    SET amount = EXCLUDED.amount, unit = EXCLUDED.unit
                """, (recipe_id, ing['ingredient_id'], ing.get('amount', ''), ing.get('unit', '')))
            
            conn.commit()
            
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(dict(recipe), default=str),
                'isBase64Encoded': False
            }
        
        elif method == 'PUT':
            user_id = get_user_from_token(headers)
            
            if not user_id:
                return {
                    'statusCode': 401,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Authentication required'}),
                    'isBase64Encoded': False
                }
            
            body_data = json.loads(event.get('body', '{}'))
            recipe_id = body_data.get('id')
            
            if not recipe_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Recipe ID is required'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("SELECT user_id FROM recipes WHERE id = %s", (recipe_id,))
            recipe = cur.fetchone()
            
            if not recipe:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Recipe not found'}),
                    'isBase64Encoded': False
                }
            
            if recipe['user_id'] != user_id:
                return {
                    'statusCode': 403,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Access denied'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("""
                UPDATE recipes
                SET title = %s, description = %s, image_url = %s, cooking_time = %s,
                    servings = %s, difficulty = %s, category_id = %s, instructions = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, user_id, title, description, image_url, cooking_time, servings, difficulty, category_id, instructions, created_at, updated_at
            """, (
                body_data.get('title'),
                body_data.get('description', ''),
                body_data.get('image_url', ''),
                body_data.get('cooking_time'),
                body_data.get('servings'),
                body_data.get('difficulty'),
                body_data.get('category_id'),
                body_data.get('instructions'),
                recipe_id
            ))
            
            updated_recipe = cur.fetchone()
            
            if 'ingredients' in body_data:
                cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
                
                for ing in body_data['ingredients']:
                    cur.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
                        VALUES (%s, %s, %s, %s)
                    """, (recipe_id, ing['ingredient_id'], ing.get('amount', ''), ing.get('unit', '')))
            
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(dict(updated_recipe), default=str),
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
            recipe_id = params.get('id')
            
            if not recipe_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Recipe ID is required'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("SELECT user_id FROM recipes WHERE id = %s", (recipe_id,))
            recipe = cur.fetchone()
            
            if not recipe:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Recipe not found'}),
                    'isBase64Encoded': False
                }
            
            if recipe['user_id'] != user_id:
                return {
                    'statusCode': 403,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Access denied'}),
                    'isBase64Encoded': False
                }
            
            cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
            cur.execute("DELETE FROM meal_plans WHERE recipe_id = %s", (recipe_id,))
            cur.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Recipe deleted successfully'}),
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