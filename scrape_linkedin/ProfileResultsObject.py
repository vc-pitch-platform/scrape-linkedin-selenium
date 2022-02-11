import logging

from bs4 import BeautifulSoup
from .ResultsObject import ResultsObject

logger = logging.getLogger(__name__)


class ProfileResultsObject(ResultsObject):
    def __init__(self, main_profile_page, experience_page, education_page, skills_page):
        self.main_profile_soup = BeautifulSoup(main_profile_page, 'html.parser')
        self.experience_soup= BeautifulSoup(experience_page, 'html.parser')
        self.education_soup = BeautifulSoup(education_page, 'html.parser')
        self.skils_soup = BeautifulSoup(skills_page, 'html.parser')