from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import click
from notification import notify


@click.command()
@click.argument('venue_name')
@click.argument('url')
def download_initial_data(venue_name, url):
    driver = webdriver.Firefox()
    driver.get(url)
    section_headers = driver.find_elements_by_css_selector('.section__title[aria-expanded="false"]')

    for section_header in section_headers:
        section_header.click()

    with open(f'data/{venue_name}.csv', 'w') as f:
        writer = csv.writer(f)
        titles = driver.find_elements_by_css_selector('.issue-item__title')
        for title in titles:
            anchor = title.find_elements_by_tag_name('a')[0]
            link = anchor.get_attribute('href')
            paper_title = anchor.text
            writer.writerow([paper_title, link])

    driver.close()
    notify('ACM Download', 'Finished downloading data')


if __name__ == "__main__":
    download_initial_data()
