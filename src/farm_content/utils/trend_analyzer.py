"""
AI-анализ трендов и автоматическая адаптация стиля видео.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from farm_content.core import VideoProcessingError, get_logger

logger = get_logger(__name__)


class TrendAnalyzer:
    """Анализатор трендов в социальных сетях с AI-адаптацией."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.TrendAnalyzer")
        
        # Базы трендовых данных (в реальной реализации это API социальных сетей)
        self.trend_categories = {
            "visual_styles": {
                "minimalist": {
                    "score": 0.85,
                    "features": ["clean_composition", "white_space", "simple_colors"],
                    "platforms": ["instagram", "tiktok"],
                    "duration": "medium"
                },
                "neon_aesthetics": {
                    "score": 0.92,
                    "features": ["bright_colors", "glow_effects", "dark_background"],
                    "platforms": ["tiktok", "youtube_shorts"],
                    "duration": "high"
                },
                "retro_vibe": {
                    "score": 0.78,
                    "features": ["vintage_filters", "grain_effect", "warm_tones"],
                    "platforms": ["instagram", "twitter"],
                    "duration": "medium"
                },
                "dramatic_contrast": {
                    "score": 0.88,
                    "features": ["high_contrast", "dramatic_lighting", "bold_shadows"],
                    "platforms": ["tiktok", "instagram"],
                    "duration": "high"
                }
            },
            "content_themes": {
                "transformation": {
                    "score": 0.95,
                    "keywords": ["до и после", "превращение", "изменения"],
                    "engagement_rate": 0.89,
                    "viral_potential": 0.92
                },
                "behind_scenes": {
                    "score": 0.82,
                    "keywords": ["как делается", "процесс", "секреты"],
                    "engagement_rate": 0.76,
                    "viral_potential": 0.78
                },
                "tutorials": {
                    "score": 0.87,
                    "keywords": ["как сделать", "учимся", "инструкция"],
                    "engagement_rate": 0.81,
                    "viral_potential": 0.83
                },
                "challenges": {
                    "score": 0.94,
                    "keywords": ["челлендж", "вызов", "попробуй"],
                    "engagement_rate": 0.88,
                    "viral_potential": 0.91
                }
            },
            "audio_trends": {
                "trending_sounds": [
                    {
                        "name": "epic_motivation",
                        "score": 0.89,
                        "usage_count": 125000,
                        "platforms": ["tiktok", "instagram"]
                    },
                    {
                        "name": "chill_vibes",
                        "score": 0.76,
                        "usage_count": 89000,
                        "platforms": ["instagram", "youtube_shorts"]
                    },
                    {
                        "name": "dramatic_buildup",
                        "score": 0.92,
                        "usage_count": 156000,
                        "platforms": ["tiktok", "youtube_shorts"]
                    }
                ]
            },
            "timing_patterns": {
                "optimal_durations": {
                    "tiktok": {"min": 15, "max": 60, "optimal": 30},
                    "instagram": {"min": 15, "max": 90, "optimal": 45},
                    "youtube_shorts": {"min": 15, "max": 60, "optimal": 40}
                },
                "posting_times": {
                    "weekdays": ["18:00", "20:00", "22:00"],
                    "weekends": ["14:00", "16:00", "19:00"]
                }
            }
        }
        
        # Актуальные тренды (обновляются динамически)
        self.current_trends = {
            "hot_hashtags": [
                "#вирусно", "#тренд2025", "#топконтент", "#мощно",
                "#невероятно", "#смотривсе", "#рекомендации", "#популярное"
            ],
            "viral_elements": [
                "быстрый монтаж", "неожиданный поворот", "эмоциональная реакция",
                "полезная информация", "юмор", "мотивация", "лайфхак"
            ],
            "engagement_triggers": [
                "досмотри до конца", "а ты как думаешь?", "согласен лайк",
                "сохрани чтобы не потерять", "поделись с другом"
            ]
        }

    async def analyze_current_trends(
        self, 
        platforms: List[str] = ["tiktok", "instagram", "youtube_shorts"]
    ) -> Dict[str, Any]:
        """Анализ актуальных трендов."""
        
        self.logger.info("🔍 Анализ актуальных трендов...")
        
        try:
            trends_analysis = {
                "timestamp": datetime.now().isoformat(),
                "platforms_analyzed": platforms,
                "trending_styles": {},
                "content_themes": {},
                "recommendations": {}
            }
            
            # Анализ визуальных стилей
            for platform in platforms:
                platform_trends = await self._get_platform_trends(platform)
                trends_analysis["trending_styles"][platform] = platform_trends
            
            # Анализ контентных тем
            trending_themes = self._analyze_content_themes()
            trends_analysis["content_themes"] = trending_themes
            
            # Генерация рекомендаций
            recommendations = await self._generate_trend_recommendations(
                trends_analysis, platforms
            )
            trends_analysis["recommendations"] = recommendations
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа трендов: {e}")
            return self._get_fallback_trends()

    async def _get_platform_trends(self, platform: str) -> Dict[str, Any]:
        """Получение трендов для конкретной платформы."""
        
        try:
            # В реальной реализации здесь были бы API-запросы
            # Сейчас используем предустановленные данные
            
            platform_data = {
                "visual_styles": [],
                "popular_effects": [],
                "trending_duration": 30,
                "engagement_peaks": []
            }
            
            # Фильтруем стили по платформе
            for style, data in self.trend_categories["visual_styles"].items():
                if platform in data["platforms"]:
                    platform_data["visual_styles"].append({
                        "name": style,
                        "score": data["score"],
                        "features": data["features"]
                    })
            
            # Добавляем популярные эффекты
            if platform == "tiktok":
                platform_data["popular_effects"] = [
                    "speed_ramping", "zoom_transitions", "color_pop",
                    "glitch_effect", "neon_glow"
                ]
            elif platform == "instagram":
                platform_data["popular_effects"] = [
                    "smooth_transitions", "aesthetic_filters", "bokeh_blur",
                    "vintage_look", "color_grading"
                ]
            elif platform == "youtube_shorts":
                platform_data["popular_effects"] = [
                    "dynamic_zoom", "text_animations", "sound_sync",
                    "quick_cuts", "dramatic_reveals"
                ]
            
            # Оптимальная длительность
            duration_info = self.trend_categories["timing_patterns"]["optimal_durations"]
            if platform in duration_info:
                platform_data["trending_duration"] = duration_info[platform]["optimal"]
            
            return platform_data
            
        except Exception as e:
            logger.warning(f"Ошибка получения трендов для {platform}: {e}")
            return {"visual_styles": [], "popular_effects": []}

    def _analyze_content_themes(self) -> Dict[str, Any]:
        """Анализ трендовых контентных тем."""
        
        themes_analysis = {}
        
        try:
            for theme, data in self.trend_categories["content_themes"].items():
                themes_analysis[theme] = {
                    "trending_score": data["score"],
                    "engagement_potential": data["engagement_rate"],
                    "viral_potential": data["viral_potential"],
                    "keywords": data["keywords"],
                    "recommendation": self._get_theme_recommendation(theme, data)
                }
        
        except Exception as e:
            logger.warning(f"Ошибка анализа тем: {e}")
        
        return themes_analysis

    def _get_theme_recommendation(self, theme: str, data: Dict[str, Any]) -> str:
        """Генерация рекомендации для темы."""
        
        if data["score"] > 0.9:
            return f"🔥 Горячий тренд! {theme} показывает отличные результаты"
        elif data["score"] > 0.8:
            return f"📈 Растущий тренд: {theme} набирает популярность"
        elif data["score"] > 0.7:
            return f"💡 Стабильный выбор: {theme} всегда работает"
        else:
            return f"⚠️ Осторожно: {theme} теряет актуальность"

    async def _generate_trend_recommendations(
        self, 
        trends_analysis: Dict[str, Any], 
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Генерация рекомендаций на основе анализа трендов."""
        
        recommendations = {
            "top_strategies": [],
            "visual_adjustments": {},
            "content_suggestions": [],
            "timing_optimization": {}
        }
        
        try:
            # Топ стратегии
            recommendations["top_strategies"] = [
                {
                    "strategy": "Драматический контраст + быстрый монтаж",
                    "confidence": 0.92,
                    "platforms": ["tiktok", "instagram"],
                    "description": "Используйте высокий контраст и быстрые переходы"
                },
                {
                    "strategy": "Неоновая эстетика + мотивационный контент",
                    "confidence": 0.89,
                    "platforms": ["tiktok", "youtube_shorts"],
                    "description": "Яркие неоновые эффекты с мотивационными сообщениями"
                },
                {
                    "strategy": "Трансформация + челлендж элементы",
                    "confidence": 0.94,
                    "platforms": platforms,
                    "description": "Покажите преображение с элементами вызова"
                }
            ]
            
            # Визуальные корректировки для каждой платформы
            for platform in platforms:
                platform_trends = trends_analysis["trending_styles"].get(platform, {})
                visual_styles = platform_trends.get("visual_styles", [])
                
                if visual_styles:
                    top_style = max(visual_styles, key=lambda x: x["score"])
                    recommendations["visual_adjustments"][platform] = {
                        "recommended_style": top_style["name"],
                        "key_features": top_style["features"],
                        "confidence": top_style["score"]
                    }
            
            # Контентные предложения
            top_themes = sorted(
                trends_analysis["content_themes"].items(),
                key=lambda x: x[1]["trending_score"],
                reverse=True
            )[:3]
            
            for theme, data in top_themes:
                recommendations["content_suggestions"].append({
                    "theme": theme,
                    "keywords": data["keywords"],
                    "viral_potential": data["viral_potential"],
                    "implementation_tip": self._get_implementation_tip(theme)
                })
            
            # Оптимизация тайминга
            recommendations["timing_optimization"] = {
                "optimal_posting_times": self.trend_categories["timing_patterns"]["posting_times"],
                "duration_recommendations": {
                    platform: self.trend_categories["timing_patterns"]["optimal_durations"][platform]
                    for platform in platforms
                    if platform in self.trend_categories["timing_patterns"]["optimal_durations"]
                }
            }
            
        except Exception as e:
            logger.warning(f"Ошибка генерации рекомендаций: {e}")
        
        return recommendations

    def _get_implementation_tip(self, theme: str) -> str:
        """Получение совета по реализации темы."""
        
        tips = {
            "transformation": "Покажите чёткий 'до' и 'после', используйте быстрые переходы",
            "behind_scenes": "Добавьте закадровый комментарий, покажите процесс поэтапно",
            "tutorials": "Разбейте на простые шаги, добавьте текстовые подсказки",
            "challenges": "Создайте уникальный хештег, покажите пример выполнения"
        }
        
        return tips.get(theme, "Фокусируйтесь на качественном контенте и эмоциях")

    async def adapt_content_to_trends(
        self,
        content_analysis: Dict[str, Any],
        trends_analysis: Dict[str, Any],
        target_platform: str = "tiktok"
    ) -> Dict[str, Any]:
        """Адаптация контента под актуальные тренды."""
        
        self.logger.info(f"🎯 Адаптация контента под тренды {target_platform}")
        
        try:
            adaptation_plan = {
                "original_analysis": content_analysis,
                "applied_trends": [],
                "style_adjustments": {},
                "content_modifications": {},
                "estimated_improvement": 0.0
            }
            
            # Анализ совместимости с трендами
            compatibility_score = await self._calculate_trend_compatibility(
                content_analysis, trends_analysis, target_platform
            )
            
            # Применение визуальных трендов
            visual_adaptations = await self._apply_visual_trends(
                content_analysis, trends_analysis, target_platform
            )
            adaptation_plan["style_adjustments"] = visual_adaptations
            
            # Контентные модификации
            content_modifications = await self._apply_content_trends(
                content_analysis, trends_analysis
            )
            adaptation_plan["content_modifications"] = content_modifications
            
            # Расчёт ожидаемого улучшения
            improvement = await self._estimate_trend_improvement(
                compatibility_score, visual_adaptations, content_modifications
            )
            adaptation_plan["estimated_improvement"] = improvement
            
            return adaptation_plan
            
        except Exception as e:
            logger.error(f"Ошибка адаптации контента: {e}")
            raise VideoProcessingError(f"Не удалось адаптировать контент: {e}")

    async def _calculate_trend_compatibility(
        self,
        content_analysis: Dict[str, Any],
        trends_analysis: Dict[str, Any],
        platform: str
    ) -> float:
        """Расчёт совместимости контента с трендами."""
        
        try:
            compatibility_factors = []
            
            # Совместимость с визуальными стилями
            content_style = content_analysis.get("visual_style", "unknown")
            platform_trends = trends_analysis["trending_styles"].get(platform, {})
            visual_styles = platform_trends.get("visual_styles", [])
            
            style_match = any(
                style["name"] == content_style or 
                content_style in style.get("features", [])
                for style in visual_styles
            )
            compatibility_factors.append(0.8 if style_match else 0.3)
            
            # Совместимость с контентными темами
            content_type = content_analysis.get("content_type", "unknown")
            theme_scores = [
                data["trending_score"] 
                for theme, data in trends_analysis["content_themes"].items()
                if theme in content_type or content_type in theme
            ]
            
            if theme_scores:
                compatibility_factors.append(max(theme_scores))
            else:
                compatibility_factors.append(0.5)  # Нейтральная совместимость
            
            # Длительность контента
            content_duration = content_analysis.get("duration", 30)
            optimal_duration = platform_trends.get("trending_duration", 30)
            
            duration_factor = 1.0 - min(abs(content_duration - optimal_duration) / optimal_duration, 0.5)
            compatibility_factors.append(duration_factor)
            
            # Общая совместимость
            return sum(compatibility_factors) / len(compatibility_factors)
            
        except Exception as e:
            logger.warning(f"Ошибка расчёта совместимости: {e}")
            return 0.5

    async def _apply_visual_trends(
        self,
        content_analysis: Dict[str, Any],
        trends_analysis: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Применение визуальных трендов."""
        
        visual_adaptations = {
            "color_adjustments": {},
            "effect_suggestions": [],
            "composition_changes": {},
            "transition_styles": []
        }
        
        try:
            platform_trends = trends_analysis["trending_styles"].get(platform, {})
            
            # Рекомендации по цветам
            top_styles = platform_trends.get("visual_styles", [])
            if top_styles:
                best_style = max(top_styles, key=lambda x: x["score"])
                
                if "bright_colors" in best_style["features"]:
                    visual_adaptations["color_adjustments"] = {
                        "saturation": "+20%",
                        "vibrance": "+15%",
                        "highlights": "+10%"
                    }
                elif "warm_tones" in best_style["features"]:
                    visual_adaptations["color_adjustments"] = {
                        "temperature": "+200K",
                        "tint": "+5",
                        "shadows": "warmer"
                    }
            
            # Эффекты
            popular_effects = platform_trends.get("popular_effects", [])
            visual_adaptations["effect_suggestions"] = popular_effects[:3]
            
            # Композиционные изменения
            if any("clean_composition" in style.get("features", []) for style in top_styles):
                visual_adaptations["composition_changes"] = {
                    "rule_of_thirds": True,
                    "negative_space": "increase",
                    "focus_point": "center"
                }
            
        except Exception as e:
            logger.warning(f"Ошибка применения визуальных трендов: {e}")
        
        return visual_adaptations

    async def _apply_content_trends(
        self,
        content_analysis: Dict[str, Any],
        trends_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Применение контентных трендов."""
        
        content_modifications = {
            "narrative_structure": {},
            "engagement_elements": [],
            "hashtag_suggestions": [],
            "call_to_action": ""
        }
        
        try:
            # Лучшие темы
            top_themes = sorted(
                trends_analysis["content_themes"].items(),
                key=lambda x: x[1]["viral_potential"],
                reverse=True
            )[:2]
            
            # Структура повествования
            if top_themes:
                primary_theme = top_themes[0][0]
                
                if primary_theme == "transformation":
                    content_modifications["narrative_structure"] = {
                        "opening": "Покажите исходное состояние",
                        "middle": "Процесс изменения",
                        "ending": "Результат с вау-эффектом"
                    }
                elif primary_theme == "tutorials":
                    content_modifications["narrative_structure"] = {
                        "opening": "Проблема или вопрос",
                        "middle": "Пошаговое решение",
                        "ending": "Финальный результат"
                    }
            
            # Элементы вовлечения
            content_modifications["engagement_elements"] = random.sample(
                self.current_trends["engagement_triggers"], 2
            )
            
            # Хештеги
            content_modifications["hashtag_suggestions"] = random.sample(
                self.current_trends["hot_hashtags"], 5
            )
            
            # Call to action
            cta_options = [
                "Сохрани, чтобы не потерять!",
                "Поделись с друзьями!",
                "А ты как думаешь? Пиши в комментариях!",
                "Лайк, если было полезно!",
                "Подписывайся на больше контента!"
            ]
            content_modifications["call_to_action"] = random.choice(cta_options)
            
        except Exception as e:
            logger.warning(f"Ошибка применения контентных трендов: {e}")
        
        return content_modifications

    async def _estimate_trend_improvement(
        self,
        compatibility_score: float,
        visual_adaptations: Dict[str, Any],
        content_modifications: Dict[str, Any]
    ) -> float:
        """Оценка ожидаемого улучшения от применения трендов."""
        
        try:
            improvement_factors = []
            
            # Базовое улучшение от совместимости
            base_improvement = compatibility_score * 0.3
            improvement_factors.append(base_improvement)
            
            # Улучшение от визуальных адаптаций
            visual_score = 0.0
            if visual_adaptations.get("color_adjustments"):
                visual_score += 0.15
            if visual_adaptations.get("effect_suggestions"):
                visual_score += 0.1 * len(visual_adaptations["effect_suggestions"])
            
            improvement_factors.append(min(visual_score, 0.4))
            
            # Улучшение от контентных модификаций
            content_score = 0.0
            if content_modifications.get("engagement_elements"):
                content_score += 0.2
            if content_modifications.get("hashtag_suggestions"):
                content_score += 0.1
            if content_modifications.get("call_to_action"):
                content_score += 0.15
            
            improvement_factors.append(min(content_score, 0.45))
            
            # Общее улучшение
            total_improvement = sum(improvement_factors)
            return min(total_improvement, 1.0)  # Максимум 100%
            
        except Exception as e:
            logger.warning(f"Ошибка оценки улучшения: {e}")
            return 0.2  # Консервативная оценка

    def _get_fallback_trends(self) -> Dict[str, Any]:
        """Получение базовых трендов при ошибке."""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "platforms_analyzed": ["tiktok", "instagram", "youtube_shorts"],
            "trending_styles": {
                "tiktok": {
                    "visual_styles": [{"name": "neon_aesthetics", "score": 0.8}],
                    "popular_effects": ["speed_ramping", "color_pop"]
                }
            },
            "content_themes": {
                "transformation": {
                    "trending_score": 0.9,
                    "viral_potential": 0.85
                }
            },
            "recommendations": {
                "top_strategies": [
                    {
                        "strategy": "Универсальный подход",
                        "confidence": 0.7,
                        "description": "Используйте яркие цвета и быстрый монтаж"
                    }
                ]
            }
        }

    def export_trends_report(
        self, 
        trends_analysis: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """Экспорт отчёта по трендам."""
        
        try:
            report = {
                "report_generated": datetime.now().isoformat(),
                "analysis_period": "current",
                "trends_data": trends_analysis,
                "summary": {
                    "total_platforms_analyzed": len(trends_analysis.get("platforms_analyzed", [])),
                    "top_visual_trend": self._get_top_trend(trends_analysis, "visual"),
                    "top_content_theme": self._get_top_trend(trends_analysis, "content"),
                    "confidence_level": "high"
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Отчёт по трендам сохранён: {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения отчёта: {e}")

    def _get_top_trend(self, trends_analysis: Dict[str, Any], trend_type: str) -> str:
        """Получение топового тренда по типу."""
        
        try:
            if trend_type == "visual":
                styles = trends_analysis.get("trending_styles", {})
                all_styles = []
                
                for platform_styles in styles.values():
                    all_styles.extend(platform_styles.get("visual_styles", []))
                
                if all_styles:
                    top_style = max(all_styles, key=lambda x: x.get("score", 0))
                    return top_style.get("name", "неизвестно")
            
            elif trend_type == "content":
                themes = trends_analysis.get("content_themes", {})
                if themes:
                    top_theme = max(themes.items(), key=lambda x: x[1].get("trending_score", 0))
                    return top_theme[0]
            
        except Exception as e:
            logger.warning(f"Ошибка получения топового тренда: {e}")
        
        return "неизвестно"