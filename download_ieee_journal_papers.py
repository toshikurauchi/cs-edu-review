import re
import csv
import json
import click
from notification import notify
from paper import PaperData, AuthorData, dump_papers
import requests
from bs4 import BeautifulSoup
from pprint import pprint


def load_papers(venue_name):
    papers = {}
    with open(f'data/{venue_name}.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            paper = PaperData(row[0], row[1])
            papers[paper.title] = paper
    try:
        with open(f'data/{venue_name}.json', 'r') as f:
            papers_json = json.load(f)
        for paper_json in papers_json:
            p = papers[paper_json['title']]
            p.load_json(paper_json)
    except FileNotFoundError:
        pass
    return list(papers.values())


def extract_paper_data(script):
    pattern = 'xplGlobal.document.metadata='
    metadata_str = script[script.index(pattern) + len(pattern):]
    count = 0
    for i, c in enumerate(metadata_str):
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
        if count == 0:
            metadata_str = metadata_str[:i+1]
            break

    metadata = json.loads(metadata_str)

    if 'authors' in metadata:
        authors = set()
        for author in metadata['authors']:
            name = author['name']
            affiliation = ', '.join(author.get('affiliation', []))
            authors.add(AuthorData(name, affiliation))
    else:
        authors = None

    if 'keywords' in metadata:
        keywords = set()
        for keyword_dict in metadata['keywords']:
            keywords.update(keyword_dict['kwd'])
    else:
        keywords = None

    abstract = metadata.get('abstract')

    return authors, keywords, abstract


@click.command()
@click.argument('venue_name')
def download_paper_data(venue_name):
    papers = load_papers(venue_name)

    pattern = re.compile('xplGlobal.document.metadata', re.MULTILINE)
    for i, paper in enumerate(papers):
        print(f'({i+1}/{len(papers)}) {paper.title}')

        if not paper.abstract:
            page = requests.get(paper.link)

            assert page.status_code == 200
            soup = BeautifulSoup(page.content, 'html.parser')
            script = soup.find("script", text=pattern)
            authors, keywords, abstract = extract_paper_data(str(script))
            paper.abstract = abstract
            paper.authors = authors
            paper.tags = keywords
            if keywords is None or authors is None or keywords is None:
                paper.remove = True

        # Save every time (just in case). Plus it makes the time between requests more random.
        dump_papers(papers, venue_name)

    notify('IEEE Download', 'Finished downloading data')


if __name__ == "__main__":
    download_paper_data()
