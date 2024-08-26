def get_xpath(xpath: str, **kwargs):
    """
        section_id : int
        ---
        section_id must be in (1, 2)

        item_id: int
        ---
        item_id must be in (1, 100)
    """
    return xpath.format(**kwargs)


def get_page_format(page: str, **kwargs):
    """
        page_number: int
    """
    return page.format(**kwargs)
