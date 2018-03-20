#!/usr/bin/env python3.6

import sys
import subprocess
import tempfile
import io

import requests


def get_as_firefox(url: str) -> bytes:
    r = requests.get(url)
    return r.content


def download_url(url: str, output_path: str) -> None:
    data = get_as_firefox(url)
    with io.open(output_path, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    url = sys.argv[1]
    output_path = sys.argv[2]
    download_url(url, output_path)

