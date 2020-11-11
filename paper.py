from dataclasses import dataclass, field
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
    title: str = ''
    link: str = ''
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


def dump_papers(papers, venue_name):
    papers_json = [p.to_dict() for p in papers]
    with open(f'{venue_name}.json', 'w') as f:
        json.dump(papers_json, f)


