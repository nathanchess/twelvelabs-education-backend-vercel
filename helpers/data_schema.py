import pydantic

class SummarySchema(pydantic.BaseModel):
    summary: str

class PacingRecommendation(pydantic.BaseModel):
    start_time: float
    end_time: float
    recommendation: str
    severity: str

class PacingRecommendationsSchema(pydantic.BaseModel):
    recommendations: list[PacingRecommendation]

class KeyTakeawaysSchema(pydantic.BaseModel):
    key_takeaways: list[str]

class ChapterSchema(pydantic.BaseModel):
    title: str
    summary: str
    start_time: float
    end_time: float
    chapter_id: int

class ChaptersSchema(pydantic.BaseModel):
    chapters: list[ChapterSchema]

class QuizQuestion(pydantic.BaseModel):
    question: str
    answer: str
    wrong_answers: list[str]
    chapter_id: int
    answer_explanation: str
    hint: str

class QuizQuestionsSchema(pydantic.BaseModel):
    quiz_questions: list[QuizQuestion]

class Flashcard(pydantic.BaseModel):
    concept: str
    definition: str
    chapter_id: int

class FlashcardsSchema(pydantic.BaseModel):
    flashcards: list[Flashcard]

class EngagementSchema(pydantic.BaseModel):
    emotion: str
    engagement_level: int
    description: str
    reason: str
    timestamp: str

class EngagementListSchema(pydantic.BaseModel):
    engagement: list[EngagementSchema]

class TranscriptSchema(pydantic.BaseModel):
    transcript: str
    
class StudyRecommendation(pydantic.BaseModel):
    priority: str
    time_to_review: str
    recommendation_title: str
    recommendation_description: str
    recommended_chapters: list[int]

class StudyRecommendationsSchema(pydantic.BaseModel):
    study_recommendations: list[StudyRecommendation]

class ConceptMastery(pydantic.BaseModel):
    concept: str
    mastery_level: int
    chapter_title: str
    reasoning: str

class ConceptMasterySchema(pydantic.BaseModel):
    concept_mastery: list[ConceptMastery]

class MostChallengingClassTopic(pydantic.BaseModel):
    percentage_of_students_struggling: int
    topic: str
    reasoning: str

class ContentEngagement(pydantic.BaseModel):
    chapter_id: int
    engagement_level: int
    engagement_reason: str
    timestamp: str

class CourseAnalysisSchema(pydantic.BaseModel):
    most_challenging_class_topic: MostChallengingClassTopic
    recommended_action: str
    challenging_concepts: list[str]
    next_steps: str
    content_engagement: list[ContentEngagement]

class GistSchema(pydantic.BaseModel):
    title: str
    hashtags: list[str]
    topics: list[str]


__all__ = ['TranscriptSchema', 'GistSchema', 'SummarySchema', 'PacingRecommendationsSchema', 'KeyTakeawaysSchema', 'ChaptersSchema', 'QuizQuestionsSchema', 'FlashcardsSchema', 'EngagementSchema', 'EngagementListSchema']
