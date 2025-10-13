"""
Клиент для работы с HH.ru API
"""
import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class HHClient:
    """Клиент для взаимодействия с HH.ru API"""
    
    def __init__(self, token: str):
        """
        Инициализация клиента
        
        Args:
            token: Токен доступа к HH.ru API
        """
        self.token = token
        self.base_url = settings.hh_api_base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Timly/1.0 (contact@timly.ru)"
        }
    
    async def verify_token(self) -> bool:
        """
        Проверка валидности токена
        
        Returns:
            True если токен валидный, False иначе
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/me",
                    headers=self.headers
                )
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Ошибка проверки токена: {e}")
                return False
    
    async def get_employer_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получение списка активных вакансий работодателя
        
        Returns:
            Список вакансий
        """
        async with httpx.AsyncClient() as client:
            try:
                # Сначала получаем информацию о работодателе
                me_response = await client.get(
                    f"{self.base_url}/me",
                    headers=self.headers
                )
                me_response.raise_for_status()
                employer_id = me_response.json().get("employer", {}).get("id")
                
                if not employer_id:
                    logger.error("Не удалось получить ID работодателя")
                    return []
                
                # Получаем вакансии работодателя
                vacancies_response = await client.get(
                    f"{self.base_url}/employers/{employer_id}/vacancies/active",
                    headers=self.headers
                )
                vacancies_response.raise_for_status()
                
                vacancies = vacancies_response.json().get("items", [])
                return vacancies
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при получении вакансий: {e}")
                return []
            except Exception as e:
                logger.error(f"Ошибка при получении вакансий: {e}")
                return []
    
    async def get_vacancy_applications(self, vacancy_id: str) -> List[Dict[str, Any]]:
        """
        Получение откликов на вакансию
        
        Args:
            vacancy_id: ID вакансии на HH.ru
            
        Returns:
            Список откликов
        """
        async with httpx.AsyncClient() as client:
            try:
                # Получаем отклики на вакансию
                response = await client.get(
                    f"{self.base_url}/negotiations",
                    params={"vacancy_id": vacancy_id, "per_page": 100},
                    headers=self.headers
                )
                response.raise_for_status()
                
                applications = response.json().get("items", [])
                return applications
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при получении откликов: {e}")
                return []
            except Exception as e:
                logger.error(f"Ошибка при получении откликов: {e}")
                return []
    
    async def get_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение резюме кандидата
        
        Args:
            resume_id: ID резюме на HH.ru
            
        Returns:
            Данные резюме или None
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/resumes/{resume_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP ошибка при получении резюме {resume_id}: {e}")
                return None
            except Exception as e:
                logger.error(f"Ошибка при получении резюме {resume_id}: {e}")
                return None
    
    async def get_application_messages(self, application_id: str) -> List[Dict[str, Any]]:
        """
        Получение сообщений в отклике
        
        Args:
            application_id: ID отклика
            
        Returns:
            Список сообщений
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/negotiations/{application_id}/messages",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get("items", [])
                
            except Exception as e:
                logger.error(f"Ошибка при получении сообщений отклика {application_id}: {e}")
                return []