import pytest
from glob import glob

from obsidiantools.md_utils import (_get_all_wikilinks_from_html_content,
                                    _get_all_embedded_files_from_html_content,
                                    _get_unique_wikilinks,
                                    _get_all_md_link_info_from_ascii_plaintext,
                                    _get_unique_md_links_from_ascii_plaintext,
                                    _get_html_from_md_file,
                                    _get_ascii_plaintext_from_md_file, get_embedded_files,
                                    get_front_matter, get_tags, get_wikilinks)


@pytest.fixture
def html_wikilinks_stub():
    return r"""
    <pre># Intro</pre>
    This is a very basic string representation.

    ## Shopping list
    Here is a **[[Shopping list | shopping list]]**:
    - [[Bananas]]: also have these for [[Banana splits]]
    - [[Apples]]
    - [[Flour]]: not a [[Flower | flower]]

    Oh and did I say [[Bananas | BANANAS]]??
    There's no link for [Cherries].  Though there is for [[Durians]].

    ![[Egg.jpg]]

    ## Drinks
    - [[Apples|Freshly squeezed apple juice]]
    - [[Bananas|Banana smoothie]]
    - [[Protein shakes#Protein powder|Vanilla whey protein]]

    ![[Easter egg.png]]
    ![[Egg.jpg | 125]]
    """


@pytest.fixture
def txt_md_links_stub():
    return r"""
    * [The Times 03/Jan/2009 Chancellor on brink of second bailout for banks](<https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h>)
    * [Chancellor Alistair Darling on brink of second bailout for banks](<https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h>)
    * [This is a statement inside square brackets]
    * (This is a statement inside parentheses)
    * (<https://www.markdownguide.org/basic-syntax/>)[Getting the bracket types in wrong order]
    * [Markdown basic syntax - <> not in the link](https://www.markdownguide.org/basic-syntax/)
    * []()
    * [()]
    * ([])
    * [([)
    * ([)]

    [ADA](<https://cardano.org/>)
    """


@pytest.fixture
def txt_sussudio_stub():
    return _get_html_from_md_file('tests/vault-stub/Sussudio.md')


def test_get_all_wikilinks_from_html_content(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_html_content(html_wikilinks_stub)
    expected_results = ['Shopping list', 'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Bananas',
                        'Durians',
                        'Apples', 'Bananas', 'Protein shakes']

    assert actual_results == expected_results


def test_get_all_wikilinks_from_html_content_keep_aliases(html_wikilinks_stub):
    actual_results = _get_all_wikilinks_from_html_content(
        html_wikilinks_stub, remove_aliases=False)
    expected_results = ['Shopping list | shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower | flower',
                        'Bananas | BANANAS',
                        'Durians',
                        'Apples|Freshly squeezed apple juice',
                        'Bananas|Banana smoothie',
                        'Protein shakes#Protein powder|Vanilla whey protein']

    assert actual_results == expected_results


def test_get_all_embedded_files_from_html_content(html_wikilinks_stub):
    actual_results = _get_all_embedded_files_from_html_content(
        html_wikilinks_stub)
    expected_results = ['Egg.jpg', 'Easter egg.png', 'Egg.jpg']

    assert actual_results == expected_results


def test_get_all_embedded_files_from_html_content_keep_aliases(
        html_wikilinks_stub):
    actual_results = _get_all_embedded_files_from_html_content(
        html_wikilinks_stub, remove_aliases=False)
    expected_results = ['Egg.jpg', 'Easter egg.png', 'Egg.jpg | 125']

    assert actual_results == expected_results


def test_get_unique_wikilinks_from_html_content(html_wikilinks_stub):
    actual_results = _get_unique_wikilinks(
        html_wikilinks_stub, remove_aliases=True)
    expected_results = ['Shopping list',
                        'Bananas', 'Banana splits',
                        'Apples',
                        'Flour', 'Flower',
                        'Durians',
                        'Protein shakes']

    assert actual_results == expected_results
    assert isinstance(expected_results, list)


def test_get_unique_wikilinks_from_html_content_has_unique_links(html_wikilinks_stub):
    actual_links = _get_unique_wikilinks(html_wikilinks_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_get_all_md_link_info(txt_md_links_stub):
    expected_links = [('The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
                       'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ("Chancellor Alistair Darling on brink of second bailout for banks",
                      'https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h'),
                      ('ADA', 'https://cardano.org/')
                      ]
    actual_links = _get_all_md_link_info_from_ascii_plaintext(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_order_preserved(txt_md_links_stub):
    expected_links = ['https://www.thetimes.co.uk/article/chancellor-alistair-darling-on-brink-of-second-bailout-for-banks-n9l382mn62h',
                      'https://cardano.org/']
    actual_links = _get_unique_md_links_from_ascii_plaintext(txt_md_links_stub)

    assert actual_links == expected_links


def test_get_unique_md_links_has_unique_links(txt_md_links_stub):
    actual_links = _get_unique_md_links_from_ascii_plaintext(txt_md_links_stub)
    assert len(set(actual_links)) == len(actual_links)


def test_pretend_wikilink_not_extracted_from_front_matter(txt_sussudio_stub):
    actual_links = _get_unique_wikilinks(txt_sussudio_stub)
    assert not {'Polka Party!'}.issubset(set(actual_links))


def test_sussudio_front_matter():
    expected_metadata = {'title': 'Sussudio',
                         'artist': 'Phil Collins',
                         'category': 'music',
                         'year': 1985,
                         'url': 'https://www.discogs.com/Phil-Collins-Sussudio/master/106239',
                         'references': [[['American Psycho (film)']], 'Polka Party!'],
                         'chart_peaks': [{'US': 1}, {'UK': 12}]}
    actual_metadata = get_front_matter(
        'tests/vault-stub/Sussudio.md')
    assert actual_metadata == expected_metadata


def test_ne_fuit_front_matter():
    expected_metadata = {}
    actual_metadata = get_front_matter(
        'tests/vault-stub/lipsum/Ne fuit.md')
    assert actual_metadata == expected_metadata


def test_front_matter_only_parsing():
    fm_only_files = glob('tests/general/frontmatter-only*.md',
                         recursive=True)
    for f in fm_only_files:
        actual_txt = _get_ascii_plaintext_from_md_file(f)
        expected_txt = '\n'
        assert actual_txt == expected_txt


def test_separators_not_front_matter_parsing():
    files = glob('tests/general/not-frontmatter*.md',
                 recursive=True)
    for f in files:
        actual_output = get_front_matter(f)
        expected_output = {}
        assert actual_output == expected_output


def test_handle_invalid_front_matter():
    files = glob('tests/general/invalid-frontmatter*.md',
                 recursive=True)
    for f in files:
        actual_output = get_front_matter(f)
        expected_output = {}
        assert actual_output == expected_output


def test_sussudio_tags():
    actual_tags = get_tags(
        'tests/vault-stub/Sussudio.md')
    expected_tags = ['y1982', 'y_1982', 'y-1982', 'y1982', 'y2000']
    assert actual_tags == expected_tags


def test_embedded_files_alias_scaling():
    actual_embedded_images = get_embedded_files(
        'tests/general/embedded-images_in-table.md')
    expected_embedded_images = ['test-image_1_before.png',
                                'test-image_1_after.png',
                                'test-image_2_before.png',
                                'test-image_2_after.png']
    assert actual_embedded_images == expected_embedded_images


def test_wikilinks_code_block():
    actual_links = get_wikilinks(
        'tests/general/wikilinks_exclude-code.md')
    expected_links = []
    assert actual_links == expected_links
