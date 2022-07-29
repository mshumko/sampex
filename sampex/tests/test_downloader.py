from datetime import datetime
import tempfile

import pytest
import numpy as np
import requests

import sampex


def test_downloader_ls():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        'https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/State4/',
        download_dir=tmp_dir.name
        )
    paths = d.ls(match='*.txt*')
    assert len(paths) == 5568
    assert paths[0].url == ('https://izw1.caltech.edu/sampex/DataCenter/DATA/'
                            'HILThires/State4/hhrr1996220.txt.zip')
    return

def test_downloader_ls_one_file():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        ('https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/'
         'State4/'),
        download_dir=tmp_dir.name
        )
    paths = d.ls(match='hhrr1996225*')
    assert len(paths) == 1
    assert paths[0].url == ('https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/'
                            'State4/hhrr1996225.txt.zip')
    assert paths[0].name() == 'hhrr1996225.txt.zip'
    return

def test_downloader_stream():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        'https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/State4/',
        download_dir=tmp_dir.name
        )
    paths = d.ls(match='*.txt*')
    path = paths[0].download(stream=True)
    assert path.name == 'hhrr1996220.txt.zip'
    return

def test_downloader_download():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        'https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/State4/',
        download_dir=tmp_dir.name
        )
    paths = d.ls(match='*.txt*')
    path = paths[1].download(stream=False)
    assert path.name == 'hhrr1996221.txt.zip'
    return

def test_downloader_invalid_url():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        'https://cltech.edu/sampex/DataCenter/DATA/HILThires/State4/',
        download_dir=tmp_dir
        )
    with pytest.raises(requests.exceptions.ConnectionError):
        d.ls(match='*.txt*')
    return

def test_downloader_invalid_ls():
    tmp_dir = tempfile.TemporaryDirectory()    
    d = sampex.Downloader(
        ('https://izw1.caltech.edu/sampex/DataCenter/DATA/HILThires/'
        'State4/'),
        download_dir=tmp_dir
        )
    with pytest.raises(FileNotFoundError):
        d.ls(match='test')
    return