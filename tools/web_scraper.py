"""
Fashion AI Automation System - Web Scraper
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class WebScraper:
    """패션 관련 웹사이트 스크래핑 도구"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_fashion_content(self, url: str, keyword: str = "") -> Optional[Dict[str, Any]]:
        """패션 웹사이트에서 콘텐츠 스크래핑"""
        
        try:
            # 실제 환경에서는 robots.txt 확인 및 rate limiting 필요
            time.sleep(1)  # 요청 간격 조절
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 웹사이트별 맞춤 스크래핑 로직
            if "vogue" in url.lower():
                return self._scrape_vogue(soup, url, keyword)
            elif "elle" in url.lower():
                return self._scrape_elle(soup, url, keyword)
            elif "harpersbazaar" in url.lower():
                return self._scrape_harpers_bazaar(soup, url, keyword)
            else:
                return self._scrape_generic(soup, url, keyword)
                
        except requests.exceptions.RequestException as e:
            print(f"웹 스크래핑 네트워크 오류 ({url}): {str(e)}")
            return self._get_sample_content(url, keyword)
        except Exception as e:
            print(f"웹 스크래핑 오류 ({url}): {str(e)}")
            return self._get_sample_content(url, keyword)
    
    def _scrape_vogue(self, soup: BeautifulSoup, url: str, keyword: str) -> Dict[str, Any]:
        """VOGUE 웹사이트 스크래핑"""
        
        try:
            # 제목 추출
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # 본문 추출
            content_selectors = [
                '.article-content',
                '.post-content', 
                '.entry-content',
                'article',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            # 이미지 추출
            images = []
            img_tags = soup.find_all('img', src=True)
            for img in img_tags[:5]:  # 최대 5개
                img_url = img.get('src')
                if img_url and not img_url.startswith('data:'):
                    images.append(img_url)
            
            return {
                "source": "VOGUE Korea",
                "title": title,
                "content": content[:1000],  # 최대 1000자
                "url": url,
                "images": images,
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"VOGUE 스크래핑 오류: {str(e)}")
            return self._get_sample_content(url, keyword)
    
    def _scrape_elle(self, soup: BeautifulSoup, url: str, keyword: str) -> Dict[str, Any]:
        """ELLE 웹사이트 스크래핑"""
        
        try:
            # ELLE 특화 스크래핑 로직
            title_tag = soup.find('h1', class_='title') or soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # 본문 추출
            content_elem = (soup.find('div', class_='article-body') or 
                          soup.find('div', class_='content') or
                          soup.find('article'))
            
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            return {
                "source": "ELLE Korea",
                "title": title,
                "content": content[:1000],
                "url": url,
                "images": [],
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"ELLE 스크래핑 오류: {str(e)}")
            return self._get_sample_content(url, keyword)
    
    def _scrape_harpers_bazaar(self, soup: BeautifulSoup, url: str, keyword: str) -> Dict[str, Any]:
        """Harper's Bazaar 웹사이트 스크래핑"""
        
        try:
            # Harper's Bazaar 특화 스크래핑 로직
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            content_elem = soup.find('div', class_='article-content') or soup.find('article')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            return {
                "source": "Harper's Bazaar Korea",
                "title": title,
                "content": content[:1000],
                "url": url,
                "images": [],
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Harper's Bazaar 스크래핑 오류: {str(e)}")
            return self._get_sample_content(url, keyword)
    
    def _scrape_generic(self, soup: BeautifulSoup, url: str, keyword: str) -> Dict[str, Any]:
        """일반 웹사이트 스크래핑"""
        
        try:
            # 일반적인 스크래핑 로직
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # 메인 콘텐츠 영역 찾기
            content_selectors = [
                'main',
                'article', 
                '.content',
                '.post-content',
                '.article-content',
                '.entry-content',
                '#content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            # 콘텐츠가 없으면 본문에서 텍스트 추출
            if not content:
                content = soup.get_text(strip=True)
            
            return {
                "source": "Fashion Website",
                "title": title,
                "content": content[:1000],
                "url": url,
                "images": [],
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"일반 스크래핑 오류: {str(e)}")
            return self._get_sample_content(url, keyword)
    
    def _get_sample_content(self, url: str, keyword: str) -> Dict[str, Any]:
        """샘플 콘텐츠 반환 (스크래핑 실패 시)"""
        
        sample_contents = {
            "vogue": {
                "source": "VOGUE Korea",
                "title": f"2024 {keyword} 트렌드 리포트",
                "content": f"올해 {keyword} 트렌드는 지속가능성과 개성 표현에 중점을 두고 있습니다. 미니멀리즘과 맥시멀리즘이 공존하며, 개인의 취향을 자유롭게 표현할 수 있는 다양한 스타일이 주목받고 있습니다. 특히 친환경 소재와 업사이클링 패션이 큰 인기를 끌고 있으며, Z세대를 중심으로 빈티지 아이템과 현대적 디자인을 믹스 매치하는 스타일이 트렌드로 자리잡았습니다."
            },
            "elle": {
                "source": "ELLE Korea",
                "title": f"{keyword} 스타일링 가이드",
                "content": f"{keyword} 스타일링의 핵심은 균형입니다. 클래식한 아이템과 트렌디한 요소를 적절히 조화시키는 것이 중요하며, 액세서리 활용을 통해 개성을 표현할 수 있습니다. 컬러 매칭과 실루엣 조합에 신경 쓰면 더욱 세련된 룩을 연출할 수 있습니다."
            },
            "harpersbazaar": {
                "source": "Harper's Bazaar Korea",
                "title": f"럭셔리 {keyword} 컬렉션 분석",
                "content": f"이번 시즌 럭셔리 브랜드들의 {keyword} 컬렉션은 정교한 디테일과 혁신적인 소재 사용이 특징입니다. 전통적인 장인 정신과 현대적인 테크놀로지가 만나 새로운 패션 경험을 제공하고 있으며, 고객들의 라이프스타일 변화를 반영한 실용적이면서도 우아한 디자인이 돋보입니다."
            }
        }
        
        # URL에 따라 적절한 샘플 콘텐츠 선택
        if "vogue" in url.lower():
            base_content = sample_contents["vogue"]
        elif "elle" in url.lower():
            base_content = sample_contents["elle"]
        elif "harpersbazaar" in url.lower():
            base_content = sample_contents["harpersbazaar"]
        else:
            base_content = sample_contents["vogue"]  # 기본값
        
        return {
            **base_content,
            "url": url,
            "images": [],
            "keyword": keyword,
            "scraped_at": datetime.now().isoformat(),
            "note": "샘플 데이터 (실제 스크래핑 불가)"
        }
    
    def scrape_multiple_sites(self, urls: List[str], keyword: str = "") -> List[Dict[str, Any]]:
        """여러 사이트를 순차적으로 스크래핑"""
        
        results = []
        
        for url in urls:
            try:
                result = self.scrape_fashion_content(url, keyword)
                if result:
                    results.append(result)
                
                # 요청 간격 조절
                time.sleep(2)
                
            except Exception as e:
                print(f"사이트 스크래핑 오류 ({url}): {str(e)}")
                continue
        
        return results
    
    def extract_fashion_keywords(self, text: str) -> List[str]:
        """텍스트에서 패션 관련 키워드 추출"""
        
        fashion_keywords = [
            # 의류 종류
            "드레스", "원피스", "블라우스", "셔츠", "티셔츠", "니트", "스웨터",
            "자켓", "코트", "카디건", "바지", "팬츠", "스커트", "청바지", "데님",
            
            # 스타일
            "캐주얼", "포멀", "스트리트", "빈티지", "모던", "클래식", "미니멀",
            "보헤미안", "페미닌", "머스큘린", "앤드로지너스",
            
            # 트렌드
            "트렌드", "유행", "신상", "컬렉션", "시즌", "SS", "FW", "패션위크",
            
            # 색상
            "블랙", "화이트", "네이비", "베이지", "그레이", "카키", "핑크",
            "레드", "블루", "그린", "옐로우", "퍼플",
            
            # 소재
            "코튼", "린넨", "실크", "울", "니트", "레더", "데님", "체크", "스트라이프"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in fashion_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # 중복 제거
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리 및 정규화"""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수 문자 정리
        text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
        text = re.sub(r'\n+', '\n', text)  # 여러 줄바꿈을 하나로
        
        # 불필요한 문자 제거
        text = re.sub(r'[^\w\s\.,!?;:()\-\'\"\/]', '', text)
        
        return text.strip()
    
    def is_fashion_related(self, text: str, threshold: int = 3) -> bool:
        """텍스트가 패션 관련 내용인지 판단"""
        
        fashion_keywords = self.extract_fashion_keywords(text)
        return len(fashion_keywords) >= threshold 