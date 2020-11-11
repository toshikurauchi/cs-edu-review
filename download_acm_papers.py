from dataclasses import dataclass, field
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import csv
from typing import Set
import json


@dataclass
class AuthorData:
    name: str
    affiliation: str

    def __hash__(self):
        return hash(self.name + self.affiliation)

    def to_dict(self):
        return {
            'name': self.name,
            'affiliation': self.affiliation,
        }


@dataclass
class PaperData:
    title: str
    link: str
    abstract: str = ''
    authors: Set[AuthorData] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'abstract': self.abstract,
            'authors': [a.to_dict() for a in self.authors],
            'tags': [t for t in self.tags]
        }

    def load_json(self, data):
        self.title = data.get('title', self.title)
        self.link = data.get('link', self.link)
        self.abstract = data.get('abstract', self.abstract)
        self.tags = set(data.get('tags', self.tags))
        for author_data in data['authors']:
            self.authors.add(AuthorData(**author_data))


def dump_papers(papers):
    papers_json = [p.to_dict() for p in papers]
    with open('ITiCSE18.json', 'w') as f:
        json.dump(papers_json, f)


def load_papers():
    papers = {}
    with open('ITiCSE18.csv', 'r') as f:
        reader = csv.reader(f)
        for title, link in reader:
            papers[title] = PaperData(title, link)
    try:
        with open('ITiCSE18.json', 'r') as f:
            papers_json = json.load(f)
        for paper_json in papers_json:
            p = papers[paper_json['title']]
            p.load_json(paper_json)
    except FileNotFoundError:
        pass
    return list(papers.values())


papers = load_papers()

driver = webdriver.Firefox()

for i, paper in enumerate(papers):
    print(f'({i+1}/{len(papers)}) {paper.title}')
    while not paper.abstract:
        try:
            driver.get(paper.link)
            authors = driver.find_elements_by_css_selector('ul[ariaa-label="authors"]>li.loa__item .author-name')
            for author in authors:
                name = author.get_attribute('title')
                affiliation = author.find_element_by_css_selector('.loa_author_inst>p').get_attribute('innerText')
                paper.authors.add(AuthorData(name, affiliation))
            paper.abstract = driver.find_element_by_css_selector('.abstractInFull').text
            tag_anchors = driver.find_element_by_css_selector('.tags-widget__content').find_elements_by_css_selector('li>a')
            for tag_anchor in tag_anchors:
                paper.tags.add(tag_anchor.get_attribute('innerText'))
        except StaleElementReferenceException:
            print('Retrying...')

    # Save every time (just in case). Plus it makes the time between requests more random.
    dump_papers(papers)

driver.close()

