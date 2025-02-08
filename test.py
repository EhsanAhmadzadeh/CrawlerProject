from services import get_all_comments_page_html, get_comments_data
import asyncio
URL = "https://cafebazaar.ir/app/calm.sleep.headspace.relaxingsounds"



page = asyncio.run(get_all_comments_page_html(URL))

a = get_comments_data(page,1)
print(a)