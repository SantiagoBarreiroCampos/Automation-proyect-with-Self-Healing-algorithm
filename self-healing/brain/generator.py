# -- coding: utf-8 --
"""
XpathGenerator Class used to generate the xpath of a web element.
"""


class XpathGenerator:

    def _get_parent_element(self, elem, xpath):
        """
        Recursive function that builds the xpath of a BeautifulSoup web element
        navigating all the element parents until it finds an element with id
        or the root of the web page.
        :param elem:
        :param xpath:
        :return:
        """
        parent = elem.parent
        if parent is not None:
            siblings = parent.find_all(elem.name, recursive=False)
            parent_id = parent.get("id")

            if len(siblings) - 1 == 0:
                actual_elem = f"/{elem.name}" + xpath
            else:
                actual_elem = f"/{elem.name}[{1 + siblings.index(elem)}]" + xpath

            if parent_id is not None:
                xpath = f'//*[@id="{parent.get("id")}"]{actual_elem}'
            else:
                xpath = self._get_parent_element(parent, actual_elem)

        return xpath

    def from_bs_element(self, element):
        """
        Generates the xpath of a BeautifulSoup web element.
        :param element:
        :return:
        """
        element_id = element.get("id")
        xpath = ''
        if element_id:
            xpath = f'//*[@id="{element_id}"]'
        else:
            xpath = self._get_parent_element(element, xpath)
        return xpath
