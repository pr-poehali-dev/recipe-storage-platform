import { useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Calendar } from '@/components/ui/calendar'
import Icon from '@/components/ui/icon'

interface Recipe {
  id: number
  title: string
  description: string
  image_url: string
  cooking_time: number
  servings: number
  difficulty: string
  category: string
  instructions: string
}

const mockRecipes: Recipe[] = [
  {
    id: 1,
    title: 'Классический омлет',
    description: 'Нежный и воздушный омлет на завтрак',
    image_url: 'https://images.unsplash.com/photo-1608039829572-78524f79c4c7?w=800',
    cooking_time: 15,
    servings: 2,
    difficulty: 'Легко',
    category: 'Завтраки',
    instructions: '1. Взбить яйца с молоком\n2. Посолить и поперчить\n3. Вылить на разогретую сковороду\n4. Готовить на среднем огне 5-7 минут'
  },
  {
    id: 2,
    title: 'Греческий салат',
    description: 'Свежий средиземноморский салат',
    image_url: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800',
    cooking_time: 10,
    servings: 4,
    difficulty: 'Легко',
    category: 'Салаты',
    instructions: '1. Нарезать помидоры и огурцы\n2. Добавить оливки и сыр фета\n3. Заправить оливковым маслом\n4. Посыпать орегано'
  },
  {
    id: 3,
    title: 'Куриный суп',
    description: 'Домашний куриный суп с лапшой',
    image_url: 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800',
    cooking_time: 60,
    servings: 6,
    difficulty: 'Средне',
    category: 'Супы',
    instructions: '1. Отварить курицу\n2. Добавить нарезанные овощи\n3. Варить 30 минут\n4. Добавить лапшу за 10 минут до готовности'
  },
  {
    id: 4,
    title: 'Шоколадный брауни',
    description: 'Влажный шоколадный десерт',
    image_url: 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800',
    cooking_time: 45,
    servings: 8,
    difficulty: 'Средне',
    category: 'Десерты',
    instructions: '1. Растопить шоколад с маслом\n2. Смешать с сахаром и яйцами\n3. Добавить муку\n4. Выпекать 25-30 минут при 180°C'
  },
  {
    id: 5,
    title: 'Паста Карбонара',
    description: 'Классическая итальянская паста',
    image_url: 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800',
    cooking_time: 25,
    servings: 4,
    difficulty: 'Средне',
    category: 'Обеды',
    instructions: '1. Отварить спагетти\n2. Обжарить бекон\n3. Смешать яйца с сыром\n4. Соединить все ингредиенты'
  },
  {
    id: 6,
    title: 'Панкейки с ягодами',
    description: 'Пышные американские панкейки',
    image_url: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800',
    cooking_time: 20,
    servings: 4,
    difficulty: 'Легко',
    category: 'Завтраки',
    instructions: '1. Смешать сухие ингредиенты\n2. Добавить молоко и яйца\n3. Жарить на сковороде\n4. Подавать с ягодами и сиропом'
  }
]

const categories = [
  { name: 'Все рецепты', icon: 'Utensils', color: 'bg-primary' },
  { name: 'Завтраки', icon: 'Coffee', color: 'bg-accent' },
  { name: 'Обеды', icon: 'UtensilsCrossed', color: 'bg-secondary' },
  { name: 'Ужины', icon: 'CookingPot', color: 'bg-primary' },
  { name: 'Десерты', icon: 'Cake', color: 'bg-accent' },
  { name: 'Салаты', icon: 'Salad', color: 'bg-secondary' },
  { name: 'Супы', icon: 'Soup', color: 'bg-primary' }
]

export default function Index() {
  const [activeTab, setActiveTab] = useState('home')
  const [selectedCategory, setSelectedCategory] = useState('Все рецепты')
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [favorites, setFavorites] = useState<number[]>([])
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date())

  const filteredRecipes = mockRecipes.filter(recipe => {
    const matchesCategory = selectedCategory === 'Все рецепты' || recipe.category === selectedCategory
    const matchesSearch = recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          recipe.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const favoriteRecipes = mockRecipes.filter(recipe => favorites.includes(recipe.id))

  const toggleFavorite = (id: number) => {
    setFavorites(prev => 
      prev.includes(id) ? prev.filter(fav => fav !== id) : [...prev, id]
    )
  }

  const difficultyColors: Record<string, string> = {
    'Легко': 'bg-secondary text-secondary-foreground',
    'Средне': 'bg-accent text-accent-foreground',
    'Сложно': 'bg-destructive text-destructive-foreground'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-green-50 to-yellow-50">
      <header className="bg-white/90 backdrop-blur-sm border-b sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center">
                <Icon name="ChefHat" className="text-white" size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  Кулинарная книга
                </h1>
                <p className="text-sm text-muted-foreground">Ваши любимые рецепты</p>
              </div>
            </div>
            <Button className="bg-gradient-to-r from-primary to-secondary text-white hover:opacity-90">
              <Icon name="UserPlus" size={18} className="mr-2" />
              Войти
            </Button>
          </div>
        </div>
      </header>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="bg-white/80 backdrop-blur-sm border-b sticky top-[73px] z-40">
          <div className="container mx-auto px-4">
            <TabsList className="w-full justify-start gap-2 bg-transparent h-14">
              <TabsTrigger value="home" className="gap-2">
                <Icon name="Home" size={18} />
                Главная
              </TabsTrigger>
              <TabsTrigger value="recipes" className="gap-2">
                <Icon name="Book" size={18} />
                Рецепты
              </TabsTrigger>
              <TabsTrigger value="planner" className="gap-2">
                <Icon name="CalendarDays" size={18} />
                Планировщик
              </TabsTrigger>
              <TabsTrigger value="ingredients" className="gap-2">
                <Icon name="Package" size={18} />
                Ингредиенты
              </TabsTrigger>
              <TabsTrigger value="favorites" className="gap-2">
                <Icon name="Heart" size={18} />
                Избранное
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <TabsContent value="home" className="mt-0 space-y-8">
            <section className="bg-gradient-to-r from-primary via-secondary to-accent text-white rounded-3xl p-12 shadow-xl">
              <div className="max-w-2xl">
                <h2 className="text-5xl font-bold mb-4">Готовьте с удовольствием!</h2>
                <p className="text-xl mb-6 text-white/90">
                  Храните, создавайте и планируйте ваши любимые рецепты в одном месте
                </p>
                <Button size="lg" className="bg-white text-primary hover:bg-white/90 text-lg px-8">
                  <Icon name="Plus" size={20} className="mr-2" />
                  Добавить рецепт
                </Button>
              </div>
            </section>

            <section>
              <h3 className="text-3xl font-bold mb-6">Популярные рецепты</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockRecipes.slice(0, 6).map(recipe => (
                  <Card 
                    key={recipe.id} 
                    className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer border-2"
                    onClick={() => setSelectedRecipe(recipe)}
                  >
                    <div className="relative h-48 overflow-hidden">
                      <img 
                        src={recipe.image_url} 
                        alt={recipe.title}
                        className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                      />
                      <Button
                        size="icon"
                        variant="secondary"
                        className="absolute top-3 right-3 rounded-full shadow-lg"
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleFavorite(recipe.id)
                        }}
                      >
                        <Icon 
                          name="Heart" 
                          size={18} 
                          className={favorites.includes(recipe.id) ? 'fill-destructive text-destructive' : ''}
                        />
                      </Button>
                    </div>
                    <CardHeader>
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-xl">{recipe.title}</CardTitle>
                        <Badge className={difficultyColors[recipe.difficulty]}>
                          {recipe.difficulty}
                        </Badge>
                      </div>
                      <CardDescription className="line-clamp-2">{recipe.description}</CardDescription>
                    </CardHeader>
                    <CardFooter className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Icon name="Clock" size={16} />
                        {recipe.cooking_time} мин
                      </div>
                      <div className="flex items-center gap-1">
                        <Icon name="Users" size={16} />
                        {recipe.servings} порц.
                      </div>
                      <Badge variant="outline" className="ml-auto">{recipe.category}</Badge>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </section>
          </TabsContent>

          <TabsContent value="recipes" className="mt-0 space-y-6">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
              <div className="relative flex-1 max-w-md">
                <Icon name="Search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Поиск рецептов..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-12 border-2"
                />
              </div>
              <Button className="bg-gradient-to-r from-primary to-secondary text-white">
                <Icon name="Plus" size={18} className="mr-2" />
                Создать рецепт
              </Button>
            </div>

            <div className="flex gap-2 overflow-x-auto pb-2">
              {categories.map(cat => (
                <Button
                  key={cat.name}
                  variant={selectedCategory === cat.name ? 'default' : 'outline'}
                  onClick={() => setSelectedCategory(cat.name)}
                  className={selectedCategory === cat.name ? `${cat.color} text-white` : ''}
                >
                  <Icon name={cat.icon as any} size={18} className="mr-2" />
                  {cat.name}
                </Button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRecipes.map(recipe => (
                <Card 
                  key={recipe.id}
                  className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer border-2"
                  onClick={() => setSelectedRecipe(recipe)}
                >
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      src={recipe.image_url} 
                      alt={recipe.title}
                      className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    />
                    <Button
                      size="icon"
                      variant="secondary"
                      className="absolute top-3 right-3 rounded-full shadow-lg"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(recipe.id)
                      }}
                    >
                      <Icon 
                        name="Heart" 
                        size={18}
                        className={favorites.includes(recipe.id) ? 'fill-destructive text-destructive' : ''}
                      />
                    </Button>
                  </div>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-xl">{recipe.title}</CardTitle>
                      <Badge className={difficultyColors[recipe.difficulty]}>
                        {recipe.difficulty}
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2">{recipe.description}</CardDescription>
                  </CardHeader>
                  <CardFooter className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Icon name="Clock" size={16} />
                      {recipe.cooking_time} мин
                    </div>
                    <div className="flex items-center gap-1">
                      <Icon name="Users" size={16} />
                      {recipe.servings} порц.
                    </div>
                    <Badge variant="outline" className="ml-auto">{recipe.category}</Badge>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="planner" className="mt-0 space-y-6">
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl">Планировщик рациона</CardTitle>
                <CardDescription>Планируйте питание на неделю вперёд</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col lg:flex-row gap-6">
                  <div className="flex-1">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={setSelectedDate}
                      className="rounded-xl border-2 shadow-sm"
                    />
                  </div>
                  <div className="flex-1 space-y-4">
                    <div>
                      <h4 className="font-semibold mb-3 text-lg">
                        {selectedDate?.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}
                      </h4>
                      {['Завтрак', 'Обед', 'Ужин'].map(mealType => (
                        <Card key={mealType} className="mb-3">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2">
                              <Icon name="Plus" size={16} />
                              {mealType}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <Button variant="outline" className="w-full">
                              Добавить рецепт
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ingredients" className="mt-0">
            <Card className="border-2">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl">Справочник ингредиентов</CardTitle>
                    <CardDescription>Все доступные ингредиенты для рецептов</CardDescription>
                  </div>
                  <Button className="bg-gradient-to-r from-primary to-secondary text-white">
                    <Icon name="Plus" size={18} className="mr-2" />
                    Добавить
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {['Мука пшеничная', 'Сахар', 'Яйца', 'Молоко', 'Масло сливочное', 'Помидоры', 'Огурцы', 'Курица', 'Рис'].map(ing => (
                    <Card key={ing}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">{ing}</CardTitle>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="favorites" className="mt-0">
            <div>
              <h3 className="text-3xl font-bold mb-6">Избранные рецепты</h3>
              {favoriteRecipes.length === 0 ? (
                <Card className="p-12 text-center border-2 border-dashed">
                  <Icon name="Heart" size={64} className="mx-auto mb-4 text-muted-foreground" />
                  <p className="text-xl text-muted-foreground">Пока нет избранных рецептов</p>
                  <p className="text-muted-foreground mt-2">Нажмите на сердечко, чтобы добавить рецепт в избранное</p>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {favoriteRecipes.map(recipe => (
                    <Card 
                      key={recipe.id}
                      className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer border-2"
                      onClick={() => setSelectedRecipe(recipe)}
                    >
                      <div className="relative h-48 overflow-hidden">
                        <img 
                          src={recipe.image_url} 
                          alt={recipe.title}
                          className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                        />
                        <Button
                          size="icon"
                          variant="secondary"
                          className="absolute top-3 right-3 rounded-full shadow-lg"
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleFavorite(recipe.id)
                          }}
                        >
                          <Icon 
                            name="Heart" 
                            size={18}
                            className="fill-destructive text-destructive"
                          />
                        </Button>
                      </div>
                      <CardHeader>
                        <div className="flex items-start justify-between gap-2">
                          <CardTitle className="text-xl">{recipe.title}</CardTitle>
                          <Badge className={difficultyColors[recipe.difficulty]}>
                            {recipe.difficulty}
                          </Badge>
                        </div>
                        <CardDescription className="line-clamp-2">{recipe.description}</CardDescription>
                      </CardHeader>
                      <CardFooter className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Icon name="Clock" size={16} />
                          {recipe.cooking_time} мин
                        </div>
                        <div className="flex items-center gap-1">
                          <Icon name="Users" size={16} />
                          {recipe.servings} порц.
                        </div>
                        <Badge variant="outline" className="ml-auto">{recipe.category}</Badge>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </div>
      </Tabs>

      <Dialog open={!!selectedRecipe} onOpenChange={() => setSelectedRecipe(null)}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          {selectedRecipe && (
            <>
              <DialogHeader>
                <DialogTitle className="text-3xl">{selectedRecipe.title}</DialogTitle>
                <DialogDescription className="text-base">{selectedRecipe.description}</DialogDescription>
              </DialogHeader>
              <div className="space-y-6">
                <img 
                  src={selectedRecipe.image_url} 
                  alt={selectedRecipe.title}
                  className="w-full h-64 object-cover rounded-xl"
                />
                
                <div className="flex items-center gap-4 flex-wrap">
                  <Badge className={`${difficultyColors[selectedRecipe.difficulty]} text-base px-4 py-1`}>
                    {selectedRecipe.difficulty}
                  </Badge>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Icon name="Clock" size={20} />
                    <span className="text-base">{selectedRecipe.cooking_time} минут</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Icon name="Users" size={20} />
                    <span className="text-base">{selectedRecipe.servings} порций</span>
                  </div>
                  <Badge variant="outline" className="text-base px-4 py-1">{selectedRecipe.category}</Badge>
                </div>

                <div>
                  <h4 className="font-semibold text-xl mb-3">Инструкция приготовления</h4>
                  <div className="bg-muted/50 p-4 rounded-lg space-y-2">
                    {selectedRecipe.instructions.split('\n').map((step, idx) => (
                      <p key={idx} className="text-base">{step}</p>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button className="flex-1 bg-gradient-to-r from-primary to-secondary text-white">
                    <Icon name="Edit" size={18} className="mr-2" />
                    Редактировать
                  </Button>
                  <Button variant="outline" className="flex-1">
                    <Icon name="CalendarPlus" size={18} className="mr-2" />
                    В планировщик
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
