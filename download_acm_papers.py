from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import csv
import json
import click
from notification import notify
from paper import AuthorData, PaperData, dump_papers


def load_papers(venue_name):
    papers = {}
    with open(f'{venue_name}.csv', 'r') as f:
        reader = csv.reader(f)
        for title, link in reader:
            papers[title] = PaperData(title, link)
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
                try:
                    tag_anchors = driver.find_element_by_css_selector('.tags-widget__content').find_elements_by_css_selector('li>a')
                    for tag_anchor in tag_anchors:
                        paper.tags.add(tag_anchor.get_attribute('innerText'))
                except NoSuchElementException:
                    print('Could not find tags for this paper.')
            except StaleElementReferenceException:
                print('Retrying...')

        # Save every time (just in case). Plus it makes the time between requests more random.
        dump_papers(papers, venue_name)

    driver.close()
    notify('ACM Download', 'Finished downloading data')


if __name__ == "__main__":
    download_paper_data()
