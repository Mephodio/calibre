import readline # optional, will allow Up/Down/History in the console
import code
import traceback

from bs4 import BeautifulSoup
import re

# from calibre.ebooks.BeautifulSoup import BeautifulSoup

regex_num = re.compile(r'[\d._/\-ivxlcdm]+', re.IGNORECASE)

def bp(*args, **kwargs):
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()

def remove_page_titles(html):
    # traceback.print_stack()

    soup = BeautifulSoup(html, 'html.parser')

    prev_i = None
    prev_p = None
    prev_a = None
    prev_marked = False
    prev_footer = None

    cur_i = None
    cur_p = None
    cur_a = None
    cur_marked = False
    cur_footer = None

    while True:

        # print('=== iteration ===')
        list_of_p = soup.find_all('p')
        found_anything = False
        is_newpage = False

        for i in range(len(list_of_p)):
            p = list_of_p[i]
            a = check_if_tag_is_page_start(p)

            # check last line on previous page (footer)
            if a != False and i > 0:
                if cur_footer == None:
                    cur_footer = list_of_p[i - 1]
                else:
                    prev_footer = cur_footer
                    cur_footer = list_of_p[i - 1]

                    if compare_page_headers(prev_footer.text, cur_footer.text):

                        found_anything = True
                        # print(f'found footer: {prev_footer.text}')

                        prev_footer.decompose()

            if a != False or is_newpage:

                is_newpage = True
                if not p.text.strip():
                    # print('skipping line', p)
                    continue
                is_newpage = False

                if cur_i == None:
                    cur_i = i
                    cur_p = p
                    cur_a = a
                    cur_marked = False
                else:
                    if prev_marked:
                        if prev_a != False:
                            list_of_p[prev_i + 1].insert_before(prev_a)
                        # print(f'decomposing {prev_p.text}')
                        prev_p.decompose()

                    prev_i = cur_i
                    prev_p = cur_p
                    prev_a = cur_a
                    prev_marked = cur_marked

                    cur_i = i
                    cur_p = p
                    cur_a = a
                    cur_marked = False

                    # print(prev_p)
                    # print(cur_p)

                    # check first line on current page (header)
                    if compare_page_headers(prev_p.text, cur_p.text):

                        found_anything = True
                        # print('found header:', prev_p.text)

                        if prev_a != False:
                            list_of_p[prev_i + 1].insert_before(prev_a)
                        prev_p.decompose()

                        cur_marked = True

        if not found_anything:
            break



    if cur_i != None and cur_marked:
        if cur_i < len(list_of_p) - 1:
            list_of_p[cur_i + 1].insert_before(cur_a)
        # print(f'decomposing p {prev_p.text}')
        cur_p.decompose()
    if cur_footer != None:
        # print(f'decomposing footer {cur_footer.text}')
        cur_footer.decompose()


    return str(soup)


def add_nbsp_to_code(html):
    lines = html.splitlines()
    for i, line in enumerate(lines):
        pos_start = -1
        while True:
            pos_start = line.find('<code>', pos_start + 1)
            if pos_start < 0: break
            pos_end = line.find('</code>', pos_start)
            lines[i] = line[:pos_start] + line[pos_start:pos_end].replace('  ', '&#160; ') + line[pos_end:]
            print(lines[i])

    return '\n'.join(lines)


def check_if_tag_is_page_start(e):
    for a in e.findAll('a'):
        if a.has_attr('id') and len(a['id']) >= 2 and a['id'][0] == 'p' and a['id'][1] >= '0' and a['id'][1] <= '9':
            return a

    return False


def compare_page_headers(line1, line2):

    # print('comparing', line1, 'and', line2)

    line1 = regex_num.sub('\1', line1)
    line2 = regex_num.sub('\1', line2)

    return line1 == line2