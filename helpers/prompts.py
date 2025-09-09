summary_prompt = """
Summarize the video in less than 5 sentences. Listen to the audio and summarize the video in a way that is helpful for a student to understand the topic being discussed.

Ensure it follows the following data schema:

class SummarySchema(pydantic.BaseModel):
    summary: str

Response must be in JSON format. Do not include any preamble or postamble.
"""

key_takeaways_prompt = """
Generate key takeaways from the video. It should be key definitions and bullet points. 
Listen to the audio and generate key takeaways that are helpful for a student to understand the topic being discussed.

Ensure it follows the following data schema:

class KeyTakeawaysSchema(pydantic.BaseModel):
    key_takeaways: list[str]

Response must be in JSON format. Do not include any preamble or postamble.
"""

pacing_recommendations_prompt = """
Generate pacing recommendations for the video. It should be a list of recommendations for the instructor to pace the video. Listen to the audio and generate pacing recommendations that are helpful for a student to understand the topic being discussed.
It should NOT cover every single second of the video. It should be a list of recommendations for the instructor to pace the video.
Make the timestamps very short and specific.
Limit to a maximum of 7 recommendations.

Ensure it follows the following data schema:

class PacingRecommendation(pydantic.BaseModel):
    start_time: float
    end_time: float
    recommendation: str
    severity: str

class PacingRecommendationsSchema(pydantic.BaseModel):
    recommendations: list[PacingRecommendation]

Response must be in JSON format. Do not include any preamble or postamble.
"""

chapter_prompt = """
Generate chapters that covers the detailed subtopics of the video that the instructor is teaching. 
The chapter summary should break down the subtopic into easy to understand instructions, concepts, and more.
Label each chapter with an approrpriate title with the topic being discussed and methodology while being concise.
Each chapter should have a detailed start and end time. The start and end time should be in seconds.
Limit to a maximum number of 9 chapters.

Ensure it follows the following data schema:

class ChapterSchema(pydantic.BaseModel):
    title: str
    summary: str
    start_time: float
    end_time: float
    chapter_id: int

class ChaptersSchema(pydantic.BaseModel):
    chapters: list[ChapterSchema]

Response must be in JSON format. Do not include any preamble or postamble.
"""

quiz_questions_prompt = """
Generate quiz questions for the video. It should be a list of quiz questions that are helpful for a student to understand the topic being discussed.

Here are the chapters of the video:
{chapters}

Please give at maximum 3 quiz questions per chapter. You may give less than 3 questions per chapter if the chapter is short. Make sure it is not just a random question, but one that is educational and helps the student understand the topic being discussed.

Ensure it follows the following data schema:

class QuizQuestion(pydantic.BaseModel):
    question: str
    answer: str
    wrong_answers: list[str]
    chapter_id: int
    answer_explanation: str
    hint: str

class QuizQuestionsSchema(pydantic.BaseModel):
    quiz_questions: list[QuizQuestion]

Response must be in JSON format. Do not include any preamble or postamble.
"""

engagement_prompt = """
Listen to the audio and watch the video and generate a list of engagement events.
This could be events like students nodding their heads, looking confused, clapping, laughing, etc.
Do not make up any events, please only make events where there is CLEAR evidence of the student or audience being engaged in the lecture.
Do not confuse with videos or other media that are not the lecture.

Please give a maximum of 5 engagement events and a minimum of 1 engagement event.

The emotion key must be one of the following:
- happy
- sad
- angry
- surprised
- confused
- bored
Only use the above emotions and do not make up any other emotions.

Ensure it follows the following data schema:

class EngagementSchema(pydantic.BaseModel):
    emotion: str
    engagement_level: int
    description: str
    reason: str
    timestamp: str

class EngagementListSchema(pydantic.BaseModel):
    engagement: list[EngagementSchema]

Response must be in JSON format. Do not include any preamble or postamble.
"""

multimodal_transcript_prompt = """
Generate a multimodal transcript of the video that includes the audio from the video and visual description of the video if there is no words spoken at the moment.
Ensure that you listen to every single word spoken at all times and account for even stuttering or pauses.
If there is no words spoken, for example there is a slide with a picture, you should describe the picture in detail.

Limit the transcript to a maximum of 300 words. Do not scan through the whole video if it is longer than 300 words.

Ensure it follows the following data schema:

class TranscriptSchema(pydantic.BaseModel):
    transcript: str
    
Response must be in JSON format. Do not include any preamble or postamble.
"""

study_recommendations_prompt = """
Here is a lecture video transcript and chapter deconstructed:
1. Transcript: {transcript}
2. Chapters: {chapters}

Generate study recommendations based on the following questions and the ones student got wrong:
1. Quiz Questions: {quiz_questions}
2. Wrong Answers: {wrong_answers}

Give a maximum of 3 study recommendations.

Ensure it follows the following data schema:

class StudyRecommendation(pydantic.BaseModel):
    priority: str
    time_to_review: str
    recommendation_title: str
    recommendation_description: str
    recommended_chapters: list[int]

class StudyRecommendationsSchema(pydantic.BaseModel):
    study_recommendations: list[StudyRecommendation]

Response must be in JSON format. Do not include any preamble or postamble.
"""

concept_mastery_prompt = """
Here is a lecture video transcript and chapter deconstructed:
1. Transcript: {transcript}
2. Chapters: {chapters}

Generate study recommendations based on the following questions and the ones student got wrong:
1. Quiz Questions: {quiz_questions}
2. Wrong Answers: {wrong_answers}

Give details on the student's mastery of the concepts. Concepts should be high level concepts that are being discussed in the video.
Please focus on the transcript and the chapters to generate the concept mastery.
You are not confined to information in the transcript and chapters. You can use your own knowledge to generate the concept mastery.

The mastery level should be a number between 0 and 100. 0 being the lowest and 100 being the highest. Based on the student's wrong answers, give a mastery level for each concept.

Give a maximum of 3 concepts.

Ex. Talking about it's importance in industry, it's applications, etc.

Ensure it follows the following data schema:

class ConceptMastery(pydantic.BaseModel):
    concept: str
    mastery_level: int
    chapter_title: str
    reasoning: str

class ConceptMasterySchema(pydantic.BaseModel):
    concept_mastery: list[ConceptMastery]

Response must be in JSON format. Do not include any preamble or postamble.
"""

course_analysis_prompt = """
Here is a lecture video metadata and student data:
1. Video Metadata: {video_metadata}
2. Student Data: {student_data}

Generate a course analysis based on the video metadata and student data.

Content engagement should be based off engagement events, student data, and the transcript.

Ensure it follows the following data schema:

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

Response must be in JSON format. Do not include any preamble or postamble.
"""

gist_prompt = """
Generate a gist of the video. It should be a list of topics, hashtags, and title.

Ensure it follows the following data schema which is a JSON object:

{
    title: str
    hashtags: list[str]
    topics: list[str]
}

Response must be in JSON format. Do not include any preamble or postamble.
"""

__all__ = [
    "summary_prompt",
    "key_takeaways_prompt",
    "pacing_recommendations_prompt",
    "chapter_prompt",
    "quiz_questions_prompt",
    "engagement_prompt",
    "multimodal_transcript_prompt",
]