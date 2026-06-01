from typing import Annotated, Literal

from pydantic import Field

FileName = Annotated[str, Field(min_length=1, max_length=255)]
ShortText = Annotated[str, Field(min_length=8, max_length=120)]
MediumText = Annotated[str, Field(min_length=20, max_length=300)]
ReviewerArchitecture = Literal["architecture"]
