'''
Business: Meal planner operations (add, get, delete meal plans)
Args: event with httpMethod, body, queryStringParameters, headers (X-Auth-Token)
Returns: HTTP response with meal plan data or error message
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
    
    user_id = get_user_from_token(headers)
    
    if not user_id:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Authentication required'}),
            'isBase64Encoded': False
        }
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if method == 'GET':
            params = event.get('queryStringParameters') or {}
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            
            query = """
                SELECT mp.*, r.title as recipe_title, r.image_url as recipe_image,
                       r.cooking_time, r.servings
                FROM meal_plans mp
                LEFT JOIN recipes r ON mp.recipe_id = r.id
                WHERE mp.user_id = %s
            """
            params_list = [user_id]
            
            if start_date:
                query += " AND mp.meal_date >= %s"
                params_list.append(start_date)
            
            if end_date:
                query += " AND mp.meal_date <= %s"
                params_list.append(end_date)
            
            query += " ORDER BY mp.meal_date ASC, mp.meal_type ASC"
            
            cur.execute(query, params_list)
            meal_plans = cur.fetchall()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps([dict(mp) for mp in meal_plans], default=str),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            
            required_fields = ['recipe_id', 'meal_date', 'meal_type']
            for field in required_fields:
                if field not in body_data:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': f'Missing required field: {field}'}),
                        'isBase64Encoded': False
                    }
            
            try:
                cur.execute("""
                    INSERT INTO meal_plans (user_id, recipe_id, meal_date, meal_type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, meal_date, meal_type)
                    DO UPDATE SET recipe_id = EXCLUDED.recipe_id
                    RETURNING id, user_id, recipe_id, meal_date, meal_type, created_at
                """, (user_id, body_data['recipe_id'], body_data['meal_date'], body_data['meal_type']))
                
                meal_plan = cur.fetchone()
                conn.commit()
                
                return {
                    'statusCode': 201,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps(dict(meal_plan), default=str),
                    'isBase64Encoded': False
                }
            
            except Exception as e:
                conn.rollback()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': str(e)}),
                    'isBase64Encoded': False
                }
        
        elif method == 'DELETE':
            params = event.get('queryStringParameters') or {}
            meal_plan_id = params.get('id')
            meal_date = params.get('meal_date')
            meal_type = params.get('meal_type')
            
            if meal_plan_id:
                cur.execute("SELECT user_id FROM meal_plans WHERE id = %s", (meal_plan_id,))
                meal_plan = cur.fetchone()
                
                if not meal_plan:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Meal plan not found'}),
                        'isBase64Encoded': False
                    }
                
                if meal_plan['user_id'] != user_id:
                    return {
                        'statusCode': 403,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Access denied'}),
                        'isBase64Encoded': False
                    }
                
                cur.execute("DELETE FROM meal_plans WHERE id = %s", (meal_plan_id,))
            
            elif meal_date and meal_type:
                cur.execute(
                    "DELETE FROM meal_plans WHERE user_id = %s AND meal_date = %s AND meal_type = %s",
                    (user_id, meal_date, meal_type)
                )
            
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Either meal plan ID or date+type is required'}),
                    'isBase64Encoded': False
                }
            
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Meal plan deleted successfully'}),
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
