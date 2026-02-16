/**
 * Shopping category auto-detection 🏪
 *
 * Mirrors backend StoreSorter keyword mappings for client-side use.
 * Maps item names to grocery aisle categories by keyword matching.
 */

const PRODUCE = ['apple','banana','orange','lemon','lime','tomato','potato','onion','garlic','lettuce','spinach','kale','carrot','celery','pepper','cucumber','avocado','broccoli','mushroom','corn','bean','pea','herb','basil','cilantro','parsley','mint','ginger','fruit','vegetable','berry','grape','melon','mango','peach','pear','plum','strawberr','blueberr','raspberr'];
const DAIRY = ['milk','cheese','yogurt','butter','cream','egg','sour cream','cottage','mozzarella','cheddar','parmesan','ricotta'];
const MEAT = ['chicken','beef','pork','steak','ground','sausage','bacon','ham','turkey','lamb','fish','salmon','tuna','shrimp','crab','lobster','meat','seafood'];
const BAKERY = ['bread','bagel','roll','bun','croissant','muffin','tortilla','pita','cake','cookie','pie','pastry','donut'];
const FROZEN = ['frozen','ice cream','pizza','waffle'];
const BEVERAGES = ['water','juice','soda','coffee','tea','beer','wine'];
const PANTRY_ITEMS = ['rice','pasta','noodle','flour','sugar','salt','oil','vinegar','sauce','soup','can','cereal','oat','honey','syrup','spice','pepper','cinnamon','cumin','paprika','oregano','thyme'];

export function guessCategory(name: string): string {
  const n = name.toLowerCase();
  if (PRODUCE.some(k => n.includes(k))) return 'Produce';
  if (DAIRY.some(k => n.includes(k))) return 'Dairy';
  if (MEAT.some(k => n.includes(k))) return 'Meat & Seafood';
  if (BAKERY.some(k => n.includes(k))) return 'Bakery';
  if (FROZEN.some(k => n.includes(k))) return 'Frozen';
  if (BEVERAGES.some(k => n.includes(k)) && !DAIRY.some(k => n.includes(k))) return 'Beverages';
  if (PANTRY_ITEMS.some(k => n.includes(k))) return 'Pantry';
  return 'Other';
}
