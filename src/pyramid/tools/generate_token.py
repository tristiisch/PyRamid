from pickle import TRUE
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from typing import Optional, List
import requests

class DeezerTokenEmptyException(Exception):
	pass

class DeezerTokenOverflowException(Exception):
	pass

class DeezerToken:
    def __init__(self, 
                 country_name: str, 
                 flag_image: str, 
                 subscription: Optional[str], 
                 expire: date, 
                 repeat: bool, 
                 token: str, 
                 author: Optional[str]):
        self.country_name: str = country_name
        self.flag_image: str = flag_image
        self.subscription: Optional[str] = subscription
        self.expire: date = expire
        self.repeat: bool = repeat
        self.token: str = token
        self.author: Optional[str] = author

    def __repr__(self) -> str:
        return (f"DeezerToken(expire='{self.expire}', repeat={self.repeat}, subscription='{self.subscription}', token='{self.token}', "
                f"country_name='{self.country_name}', flag_image='{self.flag_image}', author='{self.author}')")

class DeezerTokenProvider:
    def __init__(self, url: str = 'https://rentry.org/firehawk52', settings: dict = {'h3_id': 'deezer-arls'}):
        self._url: str = url
        self._settings: dict = settings
        self._soup: Optional[BeautifulSoup] = None
        self._tokens: list[DeezerToken] = []

    def generate(self, force: bool = False) -> bool:
        if not force and self._soup is None:
            return False
        self._fetch()
        self._tokens = self._parse()
        return True

    def get_tokens(self) -> list[DeezerToken]:
        return self._tokens

    def get_tokens_valides(self, max_duration: Optional[timedelta] = timedelta(days=365)) -> Optional[list[DeezerToken]]:
        if not self._tokens:
            return None

        now = datetime.now().date()
        
        if max_duration is not None:
            valid_tokens = [token for token in self._tokens if max_duration >= token.expire - now]
        else:
            valid_tokens = [token for token in self._tokens if token.expire > now]
        if not valid_tokens:
            return None

        sorted_tokens = sorted(valid_tokens, key=lambda token: token.expire, reverse=True)

        return sorted_tokens

    def pop_token(self, max_duration: Optional[timedelta] = timedelta(days=365)) -> Optional[DeezerToken]:
        tokens = self.get_tokens_valides(max_duration)
        if not tokens:
            return None
        token = tokens[0]
        self._tokens.remove(token)

        return token

    def next(self) -> DeezerToken:
        refreshed = self.generate()
        token = self.pop_token()
        if not token and not refreshed:
            self.generate(True)
            token = self.pop_token()
        if not token and not refreshed:
            raise DeezerTokenOverflowException()
        if not token:
            raise DeezerTokenEmptyException("No tokens are available")
        return token

    def _fetch(self) -> None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(self._url, headers=headers)
        self._soup = BeautifulSoup(response.content, 'html.parser')

    def _parse(self) -> List[DeezerToken]:
        h3_element: Optional[BeautifulSoup] = self._soup.find('h3', id=self._settings['h3_id'])

        if not h3_element:
            return []

        table: Optional[BeautifulSoup] = h3_element.find_next('table', class_='ntable')

        if not table:
            return []

        tokens: List[DeezerToken] = []

        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')

            country_img = cells[0].find('img')
            country_name: str = country_img['title']
            flag_image: str = country_img['src']

            subscription: str = cells[1].get_text(strip=True)

            date_string: str = cells[2].get_text(strip=True)
            date_value: date = datetime.strptime(date_string, '%Y-%m-%d').date()
            repeat_img = cells[2].find('img', alt='repeat')
            repeat: bool = True if repeat_img else False

            token: str = cells[3].find('code').get_text(strip=True)

            author_img = cells[4].find('img')
            author: Optional[str] = author_img['title'] if author_img else None

            tokens.append(DeezerToken(
                country_name=country_name,
                flag_image=flag_image,
                subscription=subscription,
                expire=date_value,
                repeat=repeat,
                token=token,
                author=author
            ))

        return tokens

# Usage example
if __name__ == '__main__':

    tokenProvider = DeezerTokenProvider()
    tokenProvider.generate()

    for i in range(1, len(tokenProvider.get_tokens())):
        token = tokenProvider.pop_token()
        if not token:
            break
        print(token)
