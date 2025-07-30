from telegraph import Telegraph


def CreateTelegraph(title: str,short_name: str, content: str) -> None:
  t = Telegraph()
  t.create_account(short_name=short_name)
  r = t.create_page(
    title,
    html_content=content,
  )
  return r["url"]