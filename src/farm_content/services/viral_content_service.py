"""
🎯 ИНТЕГРАТОР ВИРУСНОГО КОНТЕНТА
===============================

Модуль для интеграции генератора вирусных видео в стиле примеров
с основной системой контент-фабрики.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.farm_content.core.viral_video_generator import ViralVideoGenerator
from multi_account_system import ContentItem


class ViralContentIntegrator:
    """Интегратор вирусного контента в основную систему"""
    
    def __init__(self):
        self.logger = logging.getLogger("ViralContentIntegrator")
        self.viral_generator = ViralVideoGenerator()
        
        # Настройки под разные типы аккаунтов
        self.account_templates = {
            "ai_video": {
                "preferred_templates": ["motivation_viral", "facts_viral"],
                "quality_level": "ultra",
                "daily_limit": 5
            },
            "trend_short": {
                "preferred_templates": ["facts_viral", "lifestyle_viral"], 
                "quality_level": "high",
                "daily_limit": 8
            },
            "movie_clip": {
                "preferred_templates": ["money_viral", "lifestyle_viral"],
                "quality_level": "ultra", 
                "daily_limit": 4
            }
        }
    
    async def create_content_for_account(
        self, 
        account_type: str, 
        account_id: str,
        custom_requirements: Dict = None
    ) -> Optional[ContentItem]:
        """Создание контента для конкретного аккаунта"""
        
        try:
            self.logger.info(f"🎬 Создание контента для аккаунта {account_id} ({account_type})")
            
            # Получаем настройки для типа аккаунта
            account_settings = self.account_templates.get(account_type, self.account_templates["ai_video"])
            
            # Выбираем шаблон
            template_name = self.select_optimal_template(account_type, custom_requirements)
            
            # Создаем видео
            video_result = await self.viral_generator.create_viral_video(
                template_name=template_name,
                custom_script=custom_requirements.get("script") if custom_requirements else None,
                target_platform=custom_requirements.get("platform", "youtube") if custom_requirements else "youtube",
                quality_level=account_settings["quality_level"]
            )
            
            if not video_result["success"]:
                self.logger.error(f"Ошибка создания видео: {video_result.get('error')}")
                return None
            
            # Преобразуем в ContentItem
            content_item = self.convert_to_content_item(video_result, account_id, account_type)
            
            self.logger.info(f"✅ Контент создан для {account_id}: {content_item.content_id}")
            return content_item
            
        except Exception as e:
            self.logger.error(f"Ошибка создания контента: {e}")
            return None
    
    def select_optimal_template(self, account_type: str, custom_requirements: Dict = None) -> str:
        """Выбор оптимального шаблона"""
        
        # Если есть кастомные требования
        if custom_requirements and "template" in custom_requirements:
            return custom_requirements["template"]
        
        # Получаем предпочитаемые шаблоны для типа аккаунта
        account_settings = self.account_templates.get(account_type, self.account_templates["ai_video"])
        preferred_templates = account_settings["preferred_templates"]
        
        # Умный выбор на основе времени суток и дня недели
        import random
        from datetime import datetime
        
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # Утром (6-12) - мотивационный контент
        if 6 <= hour <= 12 and "motivation_viral" in preferred_templates:
            return "motivation_viral"
        
        # Днем (12-18) - факты и лайфхаки  
        elif 12 <= hour <= 18 and "facts_viral" in preferred_templates:
            return "facts_viral"
        
        # Вечером (18-23) - деньги и бизнес
        elif 18 <= hour <= 23 and "money_viral" in preferred_templates:
            return "money_viral"
        
        # В остальное время - случайный из предпочитаемых
        else:
            return random.choice(preferred_templates)
    
    def convert_to_content_item(
        self, 
        video_result: Dict, 
        account_id: str, 
        account_type: str
    ) -> ContentItem:
        """Преобразование результата в ContentItem"""
        
        metadata = video_result["metadata"]
        
        return ContentItem(
            content_id=video_result["video_id"],
            account_id=account_id,
            content_type=account_type,
            file_path=video_result["file_path"],
            title=metadata["title"],
            description=metadata["description"], 
            tags=metadata["tags"],
            duration=video_result["duration"],
            quality_score=video_result["quality_score"],
            created_at=datetime.fromisoformat(video_result["created_at"]),
            metadata={
                "template_used": video_result["template_used"],
                "resolution": video_result["resolution"],
                "category": metadata["category"],
                "target_emotions": metadata["target_emotions"],
                "viral_score": metadata["viral_score"]
            }
        )
    
    async def batch_create_content(
        self, 
        accounts_config: List[Dict],
        total_videos: int = 10
    ) -> List[ContentItem]:
        """Пакетное создание контента для множества аккаунтов"""
        
        created_content = []
        
        self.logger.info(f"🏭 Начинаем пакетное создание {total_videos} видео")
        
        # Распределяем видео по аккаунтам
        for i in range(total_videos):
            account_config = accounts_config[i % len(accounts_config)]
            
            content_item = await self.create_content_for_account(
                account_type=account_config["content_type"],
                account_id=account_config["account_id"],
                custom_requirements=account_config.get("requirements")
            )
            
            if content_item:
                created_content.append(content_item)
            
            # Небольшая пауза между созданием
            await asyncio.sleep(1)
        
        self.logger.info(f"✅ Создано {len(created_content)} из {total_videos} видео")
        return created_content
    
    async def create_trending_content(self, trend_topic: str, account_configs: List[Dict]) -> List[ContentItem]:
        """Создание контента на основе трендовой темы"""
        
        trending_content = []
        
        # Генерируем скрипты на основе тренда
        trending_scripts = self.generate_trending_scripts(trend_topic)
        
        for i, account_config in enumerate(account_configs):
            script = trending_scripts[i % len(trending_scripts)]
            
            custom_requirements = {
                "script": script,
                "template": "facts_viral",  # Трендовый контент лучше идет как факты
                "platform": account_config.get("platform", "youtube")
            }
            
            content_item = await self.create_content_for_account(
                account_type=account_config["content_type"],
                account_id=account_config["account_id"], 
                custom_requirements=custom_requirements
            )
            
            if content_item:
                # Добавляем информацию о тренде в метаданные
                content_item.metadata["trend_topic"] = trend_topic
                content_item.metadata["is_trending"] = True
                trending_content.append(content_item)
        
        return trending_content
    
    def generate_trending_scripts(self, trend_topic: str) -> List[str]:
        """Генерация скриптов на основе трендовой темы"""
        
        # Шаблоны для трендового контента
        templates = [
            f"ШОКИРУЮЩАЯ правда о {trend_topic}! 99% людей этого не знают...",
            f"Что произойдет с {trend_topic} в 2025 году? Невероятные факты!",
            f"ВНИМАНИЕ! {trend_topic} изменит твою жизнь за 30 секунд!",
            f"Секрет {trend_topic}, который скрывают эксперты...",
            f"Как {trend_topic} сделает тебя миллионером? Реальная история!",
            f"СТОП! Если ты не знаешь про {trend_topic} - ты теряешь деньги!"
        ]
        
        return templates
    
    def get_performance_analytics(self, content_items: List[ContentItem]) -> Dict:
        """Аналитика производительности созданного контента"""
        
        if not content_items:
            return {"error": "Нет данных для анализа"}
        
        # Анализируем распределение по шаблонам
        template_usage = {}
        total_quality = 0
        category_distribution = {}
        
        for item in content_items:
            template = item.metadata.get("template_used", "unknown")
            category = item.metadata.get("category", "unknown")
            
            template_usage[template] = template_usage.get(template, 0) + 1
            category_distribution[category] = category_distribution.get(category, 0) + 1
            total_quality += item.quality_score
        
        avg_quality = total_quality / len(content_items)
        
        return {
            "total_videos": len(content_items),
            "average_quality_score": round(avg_quality, 3),
            "template_distribution": template_usage,
            "category_distribution": category_distribution,
            "quality_grades": {
                "excellent": len([item for item in content_items if item.quality_score >= 0.8]),
                "good": len([item for item in content_items if 0.6 <= item.quality_score < 0.8]),
                "average": len([item for item in content_items if item.quality_score < 0.6])
            },
            "recommendations": self.generate_recommendations(content_items)
        }
    
    def generate_recommendations(self, content_items: List[ContentItem]) -> List[str]:
        """Генерация рекомендаций по улучшению"""
        
        recommendations = []
        
        avg_quality = sum(item.quality_score for item in content_items) / len(content_items)
        
        if avg_quality < 0.7:
            recommendations.append("Рекомендуется улучшить качество скриптов и использовать больше вирусных элементов")
        
        if avg_quality >= 0.9:
            recommendations.append("Отличное качество! Продолжайте использовать текущую стратегию")
        
        # Анализ шаблонов
        template_scores = {}
        for item in content_items:
            template = item.metadata.get("template_used", "unknown")
            if template not in template_scores:
                template_scores[template] = []
            template_scores[template].append(item.quality_score)
        
        # Находим лучший шаблон
        if template_scores:
            best_template = max(template_scores.keys(), 
                              key=lambda t: sum(template_scores[t]) / len(template_scores[t]))
            recommendations.append(f"Шаблон '{best_template}' показывает лучшие результаты")
        
        return recommendations


# Демонстрация интеграции
async def demo_viral_integration():
    """Демонстрация интеграции вирусного генератора"""
    
    print("🎯 ДЕМОНСТРАЦИЯ ИНТЕГРАЦИИ ВИРУСНОГО КОНТЕНТА")
    print("=" * 55)
    
    integrator = ViralContentIntegrator()
    
    # Настройка тестовых аккаунтов
    test_accounts = [
        {
            "account_id": "ai_master_channel",
            "content_type": "ai_video",
            "platform": "youtube"
        },
        {
            "account_id": "trend_hunter_1", 
            "content_type": "trend_short",
            "platform": "tiktok"
        },
        {
            "account_id": "money_master",
            "content_type": "movie_clip", 
            "platform": "instagram"
        }
    ]
    
    print("🎬 Создаем контент для разных типов аккаунтов...")
    
    # Создаем контент для каждого аккаунта
    created_content = []
    
    for account in test_accounts:
        print(f"\n📱 Аккаунт: {account['account_id']} ({account['content_type']})")
        
        content_item = await integrator.create_content_for_account(
            account_type=account["content_type"],
            account_id=account["account_id"]
        )
        
        if content_item:
            created_content.append(content_item)
            print(f"✅ Создано: {content_item.title[:50]}...")
            print(f"📊 Качество: {content_item.quality_score:.1%}")
            print(f"🎯 Шаблон: {content_item.metadata.get('template_used')}")
        else:
            print("❌ Ошибка создания контента")
    
    # Аналитика результатов
    if created_content:
        print(f"\n📊 АНАЛИТИКА СОЗДАННОГО КОНТЕНТА:")
        analytics = integrator.get_performance_analytics(created_content)
        
        print(f"📈 Всего видео: {analytics['total_videos']}")
        print(f"🏆 Средняя оценка: {analytics['average_quality_score']:.1%}")
        print(f"⭐ Отличных видео: {analytics['quality_grades']['excellent']}")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        for rec in analytics['recommendations']:
            print(f"   • {rec}")
    
    # Тестируем трендовый контент
    print(f"\n🔥 СОЗДАНИЕ ТРЕНДОВОГО КОНТЕНТА...")
    
    trending_content = await integrator.create_trending_content(
        trend_topic="ИИ и будущее",
        account_configs=test_accounts[:2]  # Берем первые 2 аккаунта
    )
    
    print(f"🔥 Создано {len(trending_content)} трендовых видео")
    
    print("\n🎉 Демонстрация завершена!")


if __name__ == "__main__":
    asyncio.run(demo_viral_integration())