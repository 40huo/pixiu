from lxml.html.clean import Cleaner


def html_clean(html_content):
    """
    清理HTML中的无用样式、脚本等
    :return:
    """
    cleaner = Cleaner(
        style=True,
        scripts=True,
        comments=True,
        javascript=True,
        page_structure=False,
        safe_attrs_only=True
    )
    return cleaner.clean_html(html=html_content)
