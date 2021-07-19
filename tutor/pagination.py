from flask_paginate import Pagination


def default_pagination(page, total, q, search=False):
    if len(q) > 0:
        search = True
    return Pagination(page=page, total=total,
                      search=search,
                      per_page=get_per_page(),
                      css_framework='bootstrap4',
                      display_msg="mostrando <b>{start} - {end}</b> de <b>{total}</b> registros",
                      search_msg="<b>{found}</b> registros encontrados, mostrando <b>{start} - {end}</b>",
                      found=total)


def get_per_page():
    return 10


def get_skip(page):
    if not page:
        page = 1
    page = int(page)

    skip = 0
    if page > 1:
        skip = (page - 1) * get_per_page()
    return skip
