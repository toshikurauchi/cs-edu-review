from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import click


@click.command()
@click.argument('name')
@click.argument('url')
def download_initial_data(name, url):
    driver = webdriver.Firefox()
    driver.get(url)
    section_headers = driver.find_elements_by_css_selector('.section__title[aria-expanded="false"]')

    for section_header in section_headers:
        section_header.click()

    with open(f'{name}.csv', 'w') as f:
        writer = csv.writer(f)
        titles = driver.find_elements_by_css_selector('.issue-item__title')
        for title in titles:
            anchor = title.find_elements_by_tag_name('a')[0]
            link = anchor.get_attribute('href')
            paper_title = anchor.text
            writer.writerow([paper_title, link])

    driver.close()

if __name__ == "__main__":
    download_initial_data()
