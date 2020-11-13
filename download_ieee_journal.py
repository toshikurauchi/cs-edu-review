from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import csv
import click
from notification import notify


def load_urls(venue_name):
    urls = []
    with open('data/urls.txt') as f:
        reader = csv.reader(f)
        for row in reader:
            if venue_name in row[0]:
                urls.append(row[-1])
    return urls


@click.command()
@click.argument('venue_name')
def download_journal_data(venue_name):
    driver = webdriver.Firefox()

    papers = set()
    urls = load_urls(venue_name)
    for url in urls:
        driver.get(url)
        try:
            paper_anchors = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.List-results-items h2 a'))
            )
            for paper_anchor in paper_anchors:
                paper_title = paper_anchor.get_attribute('innerText')
                link = paper_anchor.get_attribute('href')
                papers.add((paper_title, link))
        except:
            driver.quit()

    with open(f'data/{venue_name}.csv', 'w') as f:
        writer = csv.writer(f)
        for paper in papers:
            writer.writerow(paper)

    driver.close()
    notify('IEEE Download', 'Finished downloading data')


if __name__ == "__main__":
    download_journal_data()
