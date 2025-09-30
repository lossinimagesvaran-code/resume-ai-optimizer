import pandas as pd
import random
from django.conf import settings
from typing import List, Dict, Any
import re

class FashionDatasetManager:
    """
    Manages the fashion dataset and provides intelligent filtering
    and recommendation logic based on skin tone and preferences
    """
    
    def __init__(self):
        self.df = None
        self.load_dataset()
        
        # Color mapping for better matching
        self.color_mapping = {
            'Navy': ['Navy', 'Navy Blue', 'Blue'],
            'Black': ['Black'],
            'White': ['White', 'Ivory', 'Cream'],
            'Grey': ['Grey', 'Gray', 'Charcoal'],
            'Brown': ['Brown', 'Tan', 'Beige', 'Sand'],
            'Blue': ['Blue', 'Navy', 'Navy Blue'],
            'Green': ['Green', 'Olive', 'Sage'],
            'Red': ['Red', 'Burgundy', 'Rose'],
            'Pink': ['Pink', 'Rose'],
            'Purple': ['Purple'],
            'Yellow': ['Yellow', 'Gold'],
            'Orange': ['Orange'],
            'Teal': ['Teal'],
            'Stone': ['Stone', 'Beige', 'Sand'],
            'Khaki': ['Khaki', 'Tan']
        }
    
    def load_dataset(self):
        """Load the fashion dataset from CSV"""
        try:
            dataset_path = settings.FASHION_DATASET_PATH
            self.df = pd.read_csv(dataset_path)
            # Clean NaN values that cause JSON issues
            self.df = self.df.fillna('')
            print(f"Loaded {len(self.df)} fashion items from dataset")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            # Try alternative path
            try:
                import os
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                alt_path = os.path.join(current_dir, 'scraped_fashion_products.csv')
                self.df = pd.read_csv(alt_path)
                # Clean NaN values that cause JSON issues
                self.df = self.df.fillna('')
                print(f"Loaded {len(self.df)} fashion items from alternative path")
            except Exception as e2:
                print(f"Error loading from alternative path: {e2}")
                self.df = pd.DataFrame()
    
    def get_recommendations(self, gender: str, recommended_colors: List[str], 
                          season: str, user_preferences: Dict = None, 
                          limit: int = 5) -> List[Dict]:
        """
        Get clothing recommendations based on gender, colors, and preferences
        """
        if self.df.empty:
            return []
        
        # Filter by gender
        filtered_df = self.df[self.df['gender'] == gender].copy()
        
        if filtered_df.empty:
            return []
        
        # For women, use broader color matching due to limited color data
        if gender.lower() == 'women':
            # Use all available items since color data is limited for women
            color_filtered_df = filtered_df
        else:
            # Filter by recommended colors (flexible matching) for men
            color_matches = []
            for color in recommended_colors:
                for dataset_color in self.color_mapping.get(color, [color]):
                    matches = filtered_df[
                        filtered_df['color'].str.contains(dataset_color, case=False, na=False)
                    ]
                    color_matches.append(matches)
            
            if color_matches:
                color_filtered_df = pd.concat(color_matches, ignore_index=True).drop_duplicates()
            else:
                # Fallback to interview-safe colors
                safe_colors = ['Navy', 'Black', 'White', 'Grey', 'Blue']
                color_filtered_df = filtered_df[
                    filtered_df['color'].isin(safe_colors)
                ]
        
        if color_filtered_df.empty:
            print(f"DEBUG: No color matches found, using fallback with {len(filtered_df)} items")
            color_filtered_df = filtered_df.head(50)  # Larger fallback for better variety
        
        professional_categories = [
            'Blazer', 'Shirt', 'Suit Trousers', 'Formal Trousers', 
            'Trousers', 'Dress', 'Shoes'
        ]
        
        # Create outfit combinations from filtered items
        outfits = self._create_outfit_combinations(
            color_filtered_df, professional_categories, limit, gender
        )
        
        # Apply user preferences if available
        if user_preferences:
            outfits = self._apply_user_preferences(outfits, user_preferences)
        
        return outfits[:limit]
    
    def _create_outfit_combinations(self, df: pd.DataFrame, 
                                  categories: List[str], limit: int, gender: str = 'Men') -> List[Dict]:
        """Create complete outfit combinations from available items"""
        outfits = []
        
        # Group by category
        category_items = {}
        for category in categories:
            items = df[df['product_category'] == category]
            if not items.empty:
                category_items[category] = items.to_dict('records')
        
        # Create outfit combinations
        for i in range(limit * 3):  # Generate more attempts for better success rate
            outfit = self._generate_single_outfit(category_items, gender)
            if outfit and len(outfit['items']) >= 1:  # At least 1 item per outfit (relaxed requirement)
                outfits.append(outfit)
                if len(outfits) >= limit:  # Stop when we have enough
                    break
        
        return outfits
    
    def _generate_single_outfit(self, category_items: Dict, gender: str = 'Men') -> Dict:
        """Generate a single complete outfit with diverse categories"""
        outfit_items = []
        total_price = 0
        colors_used = set()
        used_categories = set()
        
        # Define outfit structure for variety based on gender
        if gender.lower() == 'women':
            outfit_structure = [
                ['Shirt'],  # Professional tops for women
                ['Trousers', 'Suit Trousers'],  # Bottom options for women
                ['Shoes']  # Footwear
            ]
        else:  # Men
            outfit_structure = [
                ['Shirt'],  # Always try to include a shirt
                ['Blazer'],  # Always try to include a blazer
                ['Trousers', 'Suit Trousers', 'Formal Trousers'],  # One type of bottom
                ['Shoes', 'Accessories']  # One accessory/shoe
            ]
        
        # Try to get one item from each category group
        for i, category_group in enumerate(outfit_structure):
                
            selected_item = None
            for category in category_group:
                if category in category_items and category_items[category] and category not in used_categories:
                    available_items = [
                        item for item in category_items[category]
                        if item and item.get('image_url') and 
                        str(item.get('image_url')) != 'nan' and
                        not item.get('image_url', '').startswith('data:image/gif;base64')
                    ]
                    if available_items:
                        selected_item = random.choice(available_items)
                        used_categories.add(category)
                        break
            
            if selected_item:
                outfit_items.append({
                    'category': selected_item.get('product_category', category),
                    'name': selected_item['product_name'],
                    'color': selected_item['color'],
                    'price': selected_item['price'],
                    'brand': selected_item['brand'],
                    'image_url': selected_item['image_url'],
                    'product_url': selected_item['product_page_url'],
                    'source': selected_item['source_page']
                })
                colors_used.add(selected_item['color'].lower())
                try:
                    price_clean = re.sub(r'[^\d.]', '', str(selected_item['price']))
                    total_price += float(price_clean) if price_clean else 0
                except:
                    pass
        
        # Add complementary items
        complementary_categories = ['Shoes', 'Accessories']
        for category in complementary_categories:
            if category in category_items and category_items[category] and len(outfit_items) < 4:
                suitable_items = [
                    item for item in category_items[category]
                    if item.get('image_url') and self._colors_complement(
                        item['color'].lower(), colors_used
                    )
                ]
                if suitable_items:
                    item = random.choice(suitable_items)
                    outfit_items.append({
                        'category': category,
                        'name': item['product_name'],
                        'color': item['color'],
                        'price': item['price'],
                        'brand': item['brand'],
                        'image_url': item['image_url'],
                        'product_url': item['product_page_url'],
                        'source': item['source_page']
                    })
                    try:
                        price_clean = re.sub(r'[^\d.]', '', str(item['price']))
                        total_price += float(price_clean) if price_clean else 0
                    except:
                        pass
        
        if not outfit_items:
            return None
        
        return {
            'items': outfit_items,
            'total_price': round(total_price, 2),
            'primary_colors': list(colors_used),
            'outfit_id': f"outfit_{random.randint(1000, 9999)}"
        }
    
    def _colors_complement(self, new_color: str, existing_colors: set) -> bool:
        """Check if a new color complements existing colors in the outfit"""
        # Professional color combinations
        complementary_sets = [
            {'navy', 'white', 'grey', 'black'},
            {'black', 'white', 'grey'},
            {'brown', 'beige', 'cream', 'tan'},
            {'blue', 'white', 'grey'},
            {'green', 'brown', 'beige'},
        ]
        
        for color_set in complementary_sets:
            if new_color in color_set and any(existing in color_set for existing in existing_colors):
                return True
        
        # Always allow neutral colors
        neutral_colors = {'black', 'white', 'grey', 'navy', 'beige', 'cream'}
        if new_color in neutral_colors:
            return True
        
        return len(existing_colors) == 0  # First color always works
    
    def _apply_user_preferences(self, outfits: List[Dict], 
                               preferences: Dict) -> List[Dict]:
        """Apply user preferences to prioritize liked items and avoid disliked ones"""
        liked_colors = preferences.get('liked_colors', [])
        disliked_colors = preferences.get('disliked_colors', [])
        liked_brands = preferences.get('liked_brands', [])
        disliked_brands = preferences.get('disliked_brands', [])
        
        scored_outfits = []
        
        for outfit in outfits:
            score = 0
            
            # Score based on colors
            for item in outfit['items']:
                item_color = item['color'].lower()
                if any(liked in item_color for liked in liked_colors):
                    score += 2
                if any(disliked in item_color for disliked in disliked_colors):
                    score -= 3
                
                # Score based on brands
                item_brand = item['brand'].lower()
                if any(liked in item_brand for liked in liked_brands):
                    score += 1
                if any(disliked in item_brand for disliked in disliked_brands):
                    score -= 2
            
            scored_outfits.append((outfit, score))
        
        # Sort by score (highest first) and return outfits
        scored_outfits.sort(key=lambda x: x[1], reverse=True)
        return [outfit for outfit, score in scored_outfits]
    
    def get_alternative_recommendations(self, gender: str, avoided_colors: List[str],
                                     season: str, limit: int = 3) -> List[Dict]:
        """Get alternative recommendations avoiding certain colors"""
        if self.df.empty:
            return []
        
        # Get season-appropriate colors excluding avoided ones
        season_colors = self._get_season_colors(season)
        alternative_colors = [
            color for color in season_colors 
            if not any(avoid.lower() in color.lower() for avoid in avoided_colors)
        ]
        
        return self.get_recommendations(
            gender, alternative_colors, season, limit=limit
        )
    
    def _get_season_colors(self, season: str) -> List[str]:
        """Get colors appropriate for each season"""
        season_palettes = {
            'spring': ['Coral', 'Peach', 'Light Blue', 'Cream', 'Light Green', 'Navy'],
            'summer': ['Powder Blue', 'Soft Pink', 'Lavender', 'Grey', 'Navy', 'White'],
            'autumn': ['Olive Green', 'Brown', 'Terracotta', 'Cream', 'Navy', 'Teal'],
            'winter': ['Navy', 'Black', 'White', 'Grey', 'Red', 'Purple']
        }
        return season_palettes.get(season, season_palettes['winter'])
    
    def search_by_criteria(self, gender: str, category: str = None, 
                          color: str = None, brand: str = None, 
                          max_price: float = None) -> List[Dict]:
        """Search items by specific criteria"""
        if self.df.empty:
            return []
        
        filtered_df = self.df[self.df['gender'] == gender].copy()
        
        if category:
            filtered_df = filtered_df[
                filtered_df['product_category'].str.contains(category, case=False, na=False)
            ]
        
        if color:
            filtered_df = filtered_df[
                filtered_df['color'].str.contains(color, case=False, na=False)
            ]
        
        if brand:
            filtered_df = filtered_df[
                filtered_df['brand'].str.contains(brand, case=False, na=False)
            ]
        
        if max_price:
            # Clean price data and filter
            def clean_price(price_str):
                try:
                    return float(re.sub(r'[^\d.]', '', str(price_str)))
                except:
                    return float('inf')
            
            filtered_df = filtered_df[
                filtered_df['price'].apply(clean_price) <= max_price
            ]
        
        return filtered_df.head(10).to_dict('records')
