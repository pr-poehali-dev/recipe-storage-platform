-- Создание таблиц для кулинарного сайта

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица категорий рецептов
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица ингредиентов
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    calories_per_100g DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица рецептов
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_url TEXT,
    cooking_time INTEGER NOT NULL,
    servings INTEGER NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    instructions TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица связи рецептов и ингредиентов
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id),
    ingredient_id INTEGER REFERENCES ingredients(id),
    amount DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    UNIQUE(recipe_id, ingredient_id)
);

-- Таблица избранных рецептов
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, recipe_id)
);

-- Таблица планировщика рациона
CREATE TABLE IF NOT EXISTS meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    plan_date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_category_id ON recipes(category_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date ON meal_plans(user_id, plan_date);

-- Вставка начальных категорий
INSERT INTO categories (name, slug, icon) VALUES
    ('Завтраки', 'breakfast', '🍳'),
    ('Обеды', 'lunch', '🍽️'),
    ('Ужины', 'dinner', '🍲'),
    ('Десерты', 'desserts', '🍰'),
    ('Салаты', 'salads', '🥗'),
    ('Супы', 'soups', '🍜'),
    ('Выпечка', 'baking', '🥖'),
    ('Напитки', 'drinks', '🥤')
ON CONFLICT (slug) DO NOTHING;

-- Вставка примерных ингредиентов
INSERT INTO ingredients (name, unit, calories_per_100g) VALUES
    ('Мука пшеничная', 'г', 364),
    ('Сахар', 'г', 387),
    ('Яйца', 'шт', 157),
    ('Молоко', 'мл', 60),
    ('Масло сливочное', 'г', 717),
    ('Соль', 'г', 0),
    ('Помидоры', 'г', 18),
    ('Огурцы', 'г', 15),
    ('Курица', 'г', 165),
    ('Рис', 'г', 130),
    ('Картофель', 'г', 77),
    ('Лук репчатый', 'г', 40),
    ('Морковь', 'г', 35),
    ('Чеснок', 'зуб', 149),
    ('Перец болгарский', 'г', 27)
ON CONFLICT DO NOTHING;

-- Вставка примерных рецептов (для демонстрации)
INSERT INTO recipes (user_id, title, description, image_url, cooking_time, servings, difficulty, category_id, instructions) VALUES
    (NULL, 'Классический омлет', 'Нежный и воздушный омлет на завтрак', 'https://images.unsplash.com/photo-1608039829572-78524f79c4c7?w=800', 15, 2, 'easy', 1, '1. Взбить яйца с молоком
2. Посолить и поперчить
3. Вылить на разогретую сковороду
4. Готовить на среднем огне 5-7 минут'),
    (NULL, 'Греческий салат', 'Свежий средиземноморский салат', 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800', 10, 4, 'easy', 5, '1. Нарезать помидоры и огурцы
2. Добавить оливки и сыр фета
3. Заправить оливковым маслом
4. Посыпать орегано'),
    (NULL, 'Куриный суп', 'Домашний куриный суп с лапшой', 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800', 60, 6, 'medium', 6, '1. Отварить курицу
2. Добавить нарезанные овощи
3. Варить 30 минут
4. Добавить лапшу за 10 минут до готовности'),
    (NULL, 'Шоколадный брауни', 'Влажный шоколадный десерт', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800', 45, 8, 'medium', 4, '1. Растопить шоколад с маслом
2. Смешать с сахаром и яйцами
3. Добавить муку
4. Выпекать 25-30 минут при 180°C')
ON CONFLICT DO NOTHING;