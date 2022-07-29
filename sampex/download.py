from typing import List
import pathlib
import urllib
import re

from bs4 import BeautifulSoup
import requests


class Downloader:
    def __init__(self, url:str) -> None:
        """
        Handles traversing the directory structure on a server and download files.

        Parameters
        ----------
        url: str
            The dataset URL.

        Example
        -------
        d = Download(
            'https://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/stream0/'
            )
        d.find_file(
            ['2014', '05', '05', 'gill*', 'ut05', '20140505_0505_gill*.pgm.gz']
            )
        d.download()
        """
        self.url = url
        return

    def ls(self, match='*'):
        """
        List files and folders in self.url. 

        Parameters
        ----------
        match: str
            An optional string pattern to match.
        
        Return
        ------
        list
            A list of full URLs.
        """
        # Check that the server status code is not
        # between 400-599 (error).
        r = requests.get(self.url)
        status_code = r.status_code
        if status_code // 100 in [4, 5]:
            raise ConnectionError(f'{self.url} returned a {status_code} error response.')
        
        matched_hrefs = self._search_hrefs(self.url, match=match)
        cls = type(self)
        downloaders = [None]*len(matched_hrefs)
        for i, matched_href in enumerate(matched_hrefs):
            new_url = urllib.parse.urljoin(self.url, matched_href, allow_fragments=True)
            downloaders[i] = cls(new_url)
        return downloaders

    # def download(self, save_dir, overwrite=False) -> None:
    #     """
    #     Downloads (streams) a file from self.url to the save_dir directory. I decided
    #     to use streaming so that a large file wont overwhelm the user's RAM.
    #     Parameters
    #     ----------
    #     save_dir: str or pathlib.Path
    #         The parent directory where to save the data to.
    #     overwrite: bool
    #         Will download overwrite an existing file. 
    #     Returns
    #     -------
    #     list
    #         A list of local paths where the data was saved to. 
    #     """
    #     save_dir = pathlib.Path(save_dir)
    #     save_dir.mkdir(parents=True, exist_ok=True)
    #     self.save_path = []

    #     for url in self.url:
    #         save_name = url.split('/')[-1]
    #         _save_path = save_dir / save_name
    #         self.save_path.append(_save_path)

    #         if (_save_path.exists()) and (not overwrite):
    #             continue

    #         r = requests.get(url, stream=True)
    #         file_size = int(r.headers.get('content-length'))
    #         downloaded_bites = 0

    #         megabyte = 1024 * 1024

    #         with open(_save_path, 'wb') as f:
    #             for data in r.iter_content(chunk_size=5*megabyte):
    #                 f.write(data)
    #                 # Update the downloaded % in the terminal.
    #                 downloaded_bites += len(data)
    #                 download_percent = round(100 * downloaded_bites / file_size)
    #                 download_str = "#" * (download_percent // 5)
    #                 print(f'Downloading {save_name}: |{download_str:<20}| {download_percent}%', end='\r')
    #         print()  # Add a newline
    #     return self.save_path


    def _search_hrefs(self, url: str, match: str='*') -> List[str]:
        """
        Given a url string, find all hyper references matching the 
        string match. The re module does the matching.
        
        Parameters
        ----------
        url: str
            A url
        match: str (optional)
            The regex match to compare the hyper references to. The default is
            to match everything (a wildcard)

        Returns
        -------
        List(str)
            A list of hyper references that matched the match string.

        Raises
        ------
        FileNotFoundError
            If no hyper references were found.
        """
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')

        match = match.replace('*', '.*')  # regex wildcard
        href_objs = soup.find_all('a', href=re.compile(match))
        # I found "?" to be in the column names so we should ignore them.
        matched_hrefs = [href_obj['href'] for href_obj in href_objs 
                    if href_obj['href'].find('?')==-1]
        if len(matched_hrefs) == 0:
            raise FileNotFoundError(
                f'The url {url} does not contain any hyper '
                f'references containing the match kwarg="{match}".'
            )
        return matched_hrefs

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}(' + self.url + ')'
    
    def __str__(self) -> str:
        return f'{self.__class__.__qualname__} with url={self.url}'

if __name__ == '__main__':
    d = Downloader(
        'https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/State4/'
        )
    # d.find_file(['2014', '05', '05', 'gill*', 'ut05', '20140505_0505_gill*.pgm.gz'])
    paths = d.ls(match='*.txt*')
    d.download() 