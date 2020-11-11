import json
import click
from notification import notify
from paper import PaperData, dump_papers
from bs4 import BeautifulSoup
import requests


def load_papers(venue_name):
    papers = {}
    with open(f'{venue_name}.txt', 'r') as f:
        count = 0
        latest_paper = None
        for row in f:
            row = row.strip()
            if not row:
                count = 0
                continue
            if count == 0:
                title = row[row.index('"')+1:row.rindex('"')-1]
                latest_paper = PaperData(title)
                papers[title] = latest_paper
            elif count == 2:
                keywords = row[row.index('{')+1:-1].split(';')
                latest_paper.tags.update(keywords)
            elif count == 3:
                url = row[row.index(' ')+1:]
                latest_paper.link = url
            count += 1
    try:
        with open(f'{venue_name}.json', 'r') as f:
            papers_json = json.load(f)
        for paper_json in papers_json:
            p = papers[paper_json['title']]
            p.load_json(paper_json)
    except FileNotFoundError:
        pass
    return list(papers.values())


@click.command()
@click.argument('venue_name')
def download_paper_data(venue_name):
    papers = load_papers(venue_name)
    print(papers)

    for i, paper in enumerate(papers):
        print(f'({i+1}/{len(papers)}) {paper.title}')

        page = requests.get(paper.link)
        print(page)
        break

        # Save every time (just in case). Plus it makes the time between requests more random.
        dump_papers(papers, venue_name)

    # notify('IEEE Download', 'Finished downloading data')


if __name__ == "__main__":
    download_paper_data()
