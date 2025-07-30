# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = [
    "DraftCreateQuizResponse",
    "Quiz",
    "QuizQuestion",
    "QuizQuestionOption",
    "QuizResults",
    "QuizResultsCategory",
]


class QuizQuestionOption(BaseModel):
    correct: bool

    text: str


class QuizQuestion(BaseModel):
    options: List[QuizQuestionOption]

    question: str
    """A quiz question."""


class QuizResultsCategory(BaseModel):
    score_range: str
    """The number of questions viewers in this category got right (e.g., "1-2")."""

    title: str
    """The title of the category."""


class QuizResults(BaseModel):
    categories: List[QuizResultsCategory]

    explanation: str
    """The text the AI narrates when showing the quiz results."""

    header: str
    """The header shown at the top of the quiz results."""


class Quiz(BaseModel):
    questions: List[QuizQuestion]

    results: QuizResults


class DraftCreateQuizResponse(BaseModel):
    caption: str
    """The description shown beside the video when posted to social media."""

    quiz: Quiz

    title: str
    """The title of the video."""
