import cv2
import numpy as np
from PIL import Image
import colorsys

class SkinToneDetector:
    """
    Advanced skin tone detection using OpenCV and color analysis
    Based on Monk Scale and seasonal color theory
    """
    
    def __init__(self):
        # HSV ranges for skin detection (multiple ranges for better accuracy)
        self.skin_hsv_ranges = [
            # Light skin tones
            ([0, 20, 70], [20, 255, 255]),
            # Medium skin tones  
            ([0, 48, 80], [20, 255, 255]),
            # Darker skin tones
            ([0, 50, 50], [25, 255, 200])
        ]
    
    def detect_skin_pixels(self, image):
        """Extract skin pixels from image using HSV color space"""
        # Convert PIL Image to OpenCV format
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create combined mask for all skin tone ranges
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in self.skin_hsv_ranges:
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Extract skin pixels
        skin_pixels = cv2.bitwise_and(image, image, mask=combined_mask)
        
        return skin_pixels, combined_mask
    
    def analyze_skin_tone(self, image):
        """
        Analyze skin tone and determine seasonal color palette
        Returns: dict with skin tone classification, undertone, season, and color values
        """
        skin_pixels, mask = self.detect_skin_pixels(image)
        
        # Get non-zero pixels (actual skin pixels)
        skin_region = skin_pixels[mask > 0]
        
        if len(skin_region) == 0:
            return {
                'error': 'No skin detected in image',
                'skin_tone': 'unknown',
                'undertone': 'unknown',
                'season': 'unknown',
                'rgb_avg': [0, 0, 0],
                'hsv_avg': [0, 0, 0]
            }
        
        # Calculate average RGB values
        avg_b, avg_g, avg_r = np.mean(skin_region, axis=0)
        rgb_avg = [int(avg_r), int(avg_g), int(avg_b)]
        
        # Convert to HSV for analysis
        hsv_avg = colorsys.rgb_to_hsv(avg_r/255, avg_g/255, avg_b/255)
        hsv_avg = [int(hsv_avg[0]*360), int(hsv_avg[1]*100), int(hsv_avg[2]*100)]
        
        # Determine undertone (warm vs cool)
        undertone = self._determine_undertone(avg_r, avg_g, avg_b)
        
        # Classify skin tone based on brightness and undertone
        skin_tone = self._classify_skin_tone(hsv_avg[2], undertone)
        
        # Map to seasonal color palette
        season = self._map_to_season(skin_tone, undertone)
        
        return {
            'skin_tone': skin_tone,
            'undertone': undertone,
            'season': season,
            'rgb_avg': rgb_avg,
            'hsv_avg': hsv_avg,
            'confidence': self._calculate_confidence(skin_region)
        }
    
    def _determine_undertone(self, r, g, b):
        """Determine if skin has warm or cool undertones"""
        # Warm undertones have more red/yellow, cool have more blue/pink
        warm_score = (r + (g * 0.5)) - b
        cool_score = b + (g * 0.3) - r
        
        return 'warm' if warm_score > cool_score else 'cool'
    
    def _classify_skin_tone(self, brightness, undertone):
        """Classify skin tone based on brightness and undertone"""
        if brightness < 30:
            return 'deep_warm' if undertone == 'warm' else 'deep_cool'
        elif brightness < 50:
            return 'tan_warm' if undertone == 'warm' else 'olive_cool'
        elif brightness < 70:
            return 'medium_warm' if undertone == 'warm' else 'medium_cool'
        else:
            return 'fair_warm' if undertone == 'warm' else 'light_cool'
    
    def _map_to_season(self, skin_tone, undertone):
        """Map skin tone and undertone to seasonal color palette"""
        if undertone == 'warm':
            if skin_tone in ['fair_warm']:
                return 'spring'
            else:
                return 'autumn'
        else:  # cool undertone
            if skin_tone in ['light_cool', 'medium_cool']:
                return 'summer'
            else:
                return 'winter'
    
    def _calculate_confidence(self, skin_pixels):
        """Calculate confidence score based on amount of skin detected"""
        total_pixels = len(skin_pixels)
        if total_pixels > 1000:
            return 'high'
        elif total_pixels > 500:
            return 'medium'
        else:
            return 'low'
    
    def get_recommended_colors(self, season):
        """Get recommended colors for each season"""
        color_palettes = {
            'spring': {
                'recommended': ['Coral', 'Peach', 'Warm Yellow', 'Golden Brown', 'Bright Green', 'Aqua', 'Ivory', 'Light Navy'],
                'avoid': ['Black', 'Pure White', 'Cool Blue', 'Purple', 'Grey']
            },
            'summer': {
                'recommended': ['Lavender', 'Powder Blue', 'Soft Pink', 'Mauve', 'Gray-Blue', 'Periwinkle', 'Light Grey', 'Navy'],
                'avoid': ['Orange', 'Bright Yellow', 'Warm Brown', 'Gold', 'Black']
            },
            'autumn': {
                'recommended': ['Olive Green', 'Rust', 'Terracotta', 'Mustard Yellow', 'Warm Brown', 'Teal', 'Cream', 'Deep Navy'],
                'avoid': ['Pink', 'Cool Blue', 'Purple', 'Pure White', 'Black']
            },
            'winter': {
                'recommended': ['Pure White', 'Black', 'Navy Blue', 'Royal Purple', 'Emerald Green', 'Bright Pink', 'Red', 'Grey'],
                'avoid': ['Beige', 'Orange', 'Yellow', 'Brown', 'Peach']
            }
        }
        return color_palettes.get(season, color_palettes['winter'])
    
    def get_interview_appropriate_colors(self, season):
        """Get interview-specific color recommendations"""
        interview_colors = {
            'spring': ['Navy', 'Light Grey', 'Cream', 'Soft Blue', 'Light Pink'],
            'summer': ['Navy', 'Light Grey', 'Powder Blue', 'Soft Pink', 'Periwinkle'],
            'autumn': ['Navy', 'Warm Brown', 'Olive Green', 'Cream', 'Deep Teal'],
            'winter': ['Navy', 'Black', 'Pure White', 'Grey', 'Deep Purple']
        }
        return interview_colors.get(season, interview_colors['winter'])
