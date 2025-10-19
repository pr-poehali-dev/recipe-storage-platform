const API_URLS = {
  auth: 'https://functions.poehali.dev/182c63a6-fa95-46e0-adf5-473c4de89b07',
  recipes: 'https://functions.poehali.dev/a18121d2-cff9-4c03-99ce-f58dc84ff321',
  ingredients: 'https://functions.poehali.dev/c64213fe-b1e8-4d65-bba3-23b40f107712',
  mealPlanner: 'https://functions.poehali.dev/51ee2376-ce05-4aab-b2f3-ab62b5d57fe5'
}

export interface User {
  id: number
  email: string
  name: string
}

export interface Recipe {
  id: number
  user_id?: number
  title: string
  description: string
  image_url: string
  cooking_time: number
  servings: number
  difficulty: string
  category_id?: number
  instructions: string
  created_at?: string
  updated_at?: string
  author_name?: string
}

export interface Ingredient {
  id: number
  name: string
  unit: string
  calories_per_100g?: string
  created_at?: string
}

export interface MealPlan {
  id: number
  user_id: number
  recipe_id: number
  meal_date: string
  meal_type: string
  recipe_title?: string
  recipe_image?: string
  cooking_time?: number
  servings?: number
  created_at?: string
}

class APIClient {
  private token: string | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('auth_token', token)
      } else {
        localStorage.removeItem('auth_token')
      }
    }
  }

  getToken() {
    return this.token
  }

  private async request(url: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    if (this.token) {
      headers['X-Auth-Token'] = this.token
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    if (!response.ok && response.status !== 401 && response.status !== 409) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }))
      throw new Error(error.error || 'Request failed')
    }

    return response.json()
  }

  async register(email: string, password: string, name: string) {
    const data = await this.request(API_URLS.auth, {
      method: 'POST',
      body: JSON.stringify({ action: 'register', email, password, name })
    })
    if (data.token) {
      this.setToken(data.token)
    }
    return data
  }

  async login(email: string, password: string) {
    const data = await this.request(API_URLS.auth, {
      method: 'POST',
      body: JSON.stringify({ action: 'login', email, password })
    })
    if (data.token) {
      this.setToken(data.token)
    }
    return data
  }

  async verifyToken() {
    if (!this.token) return null
    const data = await this.request(API_URLS.auth, {
      method: 'POST',
      body: JSON.stringify({ action: 'verify', token: this.token })
    })
    return data.user || null
  }

  logout() {
    this.setToken(null)
  }

  async getRecipes(params?: { category?: string; search?: string; id?: string }): Promise<Recipe[]> {
    const url = new URL(API_URLS.recipes)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, value)
      })
    }
    return this.request(url.toString())
  }

  async getRecipe(id: number): Promise<Recipe> {
    const url = new URL(API_URLS.recipes)
    url.searchParams.append('id', id.toString())
    return this.request(url.toString())
  }

  async createRecipe(recipe: Partial<Recipe>): Promise<Recipe> {
    return this.request(API_URLS.recipes, {
      method: 'POST',
      body: JSON.stringify(recipe)
    })
  }

  async updateRecipe(recipe: Partial<Recipe> & { id: number }): Promise<Recipe> {
    return this.request(API_URLS.recipes, {
      method: 'PUT',
      body: JSON.stringify(recipe)
    })
  }

  async deleteRecipe(id: number): Promise<void> {
    const url = new URL(API_URLS.recipes)
    url.searchParams.append('id', id.toString())
    await this.request(url.toString(), { method: 'DELETE' })
  }

  async getIngredients(params?: { search?: string }): Promise<Ingredient[]> {
    const url = new URL(API_URLS.ingredients)
    if (params?.search) {
      url.searchParams.append('search', params.search)
    }
    return this.request(url.toString())
  }

  async createIngredient(ingredient: { name: string; unit?: string; calories_per_100g?: number }): Promise<Ingredient> {
    return this.request(API_URLS.ingredients, {
      method: 'POST',
      body: JSON.stringify(ingredient)
    })
  }

  async deleteIngredient(id: number): Promise<void> {
    const url = new URL(API_URLS.ingredients)
    url.searchParams.append('id', id.toString())
    await this.request(url.toString(), { method: 'DELETE' })
  }

  async getMealPlans(params?: { start_date?: string; end_date?: string }): Promise<MealPlan[]> {
    const url = new URL(API_URLS.mealPlanner)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, value)
      })
    }
    return this.request(url.toString())
  }

  async createMealPlan(mealPlan: { recipe_id: number; meal_date: string; meal_type: string }): Promise<MealPlan> {
    return this.request(API_URLS.mealPlanner, {
      method: 'POST',
      body: JSON.stringify(mealPlan)
    })
  }

  async deleteMealPlan(params: { id?: number; meal_date?: string; meal_type?: string }): Promise<void> {
    const url = new URL(API_URLS.mealPlanner)
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.append(key, value.toString())
    })
    await this.request(url.toString(), { method: 'DELETE' })
  }
}

export const api = new APIClient()
