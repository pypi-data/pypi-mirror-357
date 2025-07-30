from typing import Union, Literal, List

from pydantic import model_validator, Field
from typing_extensions import Self

from pfip.base.constant import TChunk
from pfip.base.parser.parser_model import ParseResult, AtomItem
from pfip.base.splitter.base import ChunkSplitter
from pfip.base.splitter.splitter_model import Chunk
from pfip.base.util.character_splitter import RecursiveCharacterTextSplitter


class RecursiveChunkSplitter(ChunkSplitter):
    character_text_splitter: RecursiveCharacterTextSplitter = Field(default=None, exclude=True)
    separators: list[str] = ["\n\n", "\n", "。", "．", ".", "；", ";", "，", ",", " ", ""]
    keep_separator: Union[bool, Literal["start", "end"]] = False,
    is_separator_regex: bool = False,
    strip_whitespace: bool = True,
    chunk_size: int = 500,
    chunk_overlap: int = 100

    @model_validator(mode="after")
    def init(self) -> Self:
        if not self.character_text_splitter:
            self.separators.append("[item_start]")
            self.separators.append("[item_end]")
            self.character_text_splitter = RecursiveCharacterTextSplitter(
                separators=self.separators,
                keep_separator=self.keep_separator,
                is_separator_regex=self.is_separator_regex,
                strip_whitespace=self.strip_whitespace,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

        return self

    def support(self, file_ext: str) -> bool:
        return True

    @staticmethod
    def find_item_areas(split_content: str, items: List[AtomItem], init_index: int) -> tuple[int, int]:
        """
            确定split_content涉及的起始AtomItem的范围
        """
        split_content_100_start = split_content[:100]
        split_content_100_end = split_content[-100:] if len(split_content) >= 100 else split_content

        start_index = init_index
        end_index = init_index
        # 查找起始项：匹配开头的100个字符
        for idx, item in enumerate(items):
            if idx < start_index:
                continue
            if split_content_100_start in item.full_content or item.full_content in split_content_100_start:
                start_index = idx
                break

        # 查找结束项：匹配结尾的100个字符
        for idx, item in enumerate(items):
            if idx < start_index:
                continue
            if split_content_100_end in item.full_content or item.full_content in split_content_100_end:
                end_index = idx
                break
        if start_index > end_index:
            return start_index, start_index
        return start_index, end_index


    def __call__(self, parse_result: ParseResult) -> List[Chunk]:
        split_contents = self.character_text_splitter.split_text(parse_result.content)
        chunks: List[Chunk] = []
        for split_content in split_contents:
            chunk = Chunk(
                content=split_content,
                title=parse_result.titles[0],
                items=[],
                chunk_type=TChunk.TEXT,
                start_page=1,
                end_page=1,
            )
            chunks.append(chunk)
        return chunks
