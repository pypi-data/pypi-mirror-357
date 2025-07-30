from pydantic import BaseModel

from common_py.connector.tap_proquest.models import ArticleRecord

from . import ToolOutput


class GetArticlesInput(BaseModel):
    feed_url: str
    limit: int = 15


class GetArticlesOutput(ToolOutput):
    articles: list[ArticleRecord]
