from twelvelabs import TwelveLabs
from helpers import prompts, data_schema, LectureBuilderAgent
from .llm import LLMProvider

import pydantic
from pydantic_core import from_json
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

class TwelveLabsHandler(LLMProvider):

    def __init__(self, twelve_labs_index_id: str = "", twelve_labs_video_id: str = ""):

        self.twelve_labs_client = TwelveLabs(api_key=os.getenv("TWELVE_LABS_API_KEY"))
        self.reasoning_agent = LectureBuilderAgent()

        self.twelve_labs_index_id = twelve_labs_index_id
        self.twelve_labs_video_id = twelve_labs_video_id
        
        self.indexes = dict()

        # Internal video attributes
        self.title = None
        self.hashtags = None
        self.topics = None
        self.summary = None
        self.key_takeaways = None
        self.pacing_recommendations = None
        self.chapters = None
        self.quiz_questions = None
        self.flashcards = None

    def _list_indexes(self):

        """
        
        Lists all indexes on the TwelveLabs account and populates the indexes list.
        
        """
        
        indexes = self.twelve_labs_client.index.list()
        for index in indexes:
            self.indexes[index.name] = index

        return self.indexes
    
 
    async def _process_coroutine(self, stream_type: str, prompt: str, output_queue: asyncio.Queue):
        
        """
        
        Processes a coroutine and streams the results to the output queue.
        
        """
        
        try:

            coroutine = self.twelve_labs_client.analyze_stream(video_id=self.twelve_labs_video_id, prompt=prompt)

            for chunk in coroutine:

                print(chunk)

                await output_queue.put(json.dumps({
                    "type": stream_type,
                    "content": chunk,
                    'status': 'in_progress'
                }))

            await output_queue.put(json.dumps({
                'type': stream_type,
                'chunk': None,
                'status': 'complete'
            }))

        except Exception as e:
            
            await output_queue.put(json.dumps({
                'type': stream_type,
                'chunk': None,
                'status': 'error',
                'error': str(e)
            }))
        
    async def _prompt_llm(self, prompt: str, data_schema: pydantic.BaseModel):

        try:

            response = await asyncio.to_thread(
                self.twelve_labs_client.analyze,
                video_id=self.twelve_labs_video_id,
                prompt=prompt
            )

            cleaned_data_string = response.data.replace("```json", "").replace("```", "")
            validated_data = data_schema.model_validate(from_json(cleaned_data_string, allow_partial=True))

            return validated_data.model_dump()
        
        except Exception as e:

            print(f"Error generating {data_schema.__name__}: {str(e)}")
            return response
        
    async def generate_summary(self):

        """
        
        Generates summary for the video.
        
        """

        try:

            summary = await asyncio.to_thread(
                self.twelve_labs_client.summarize,
                video_id=self.twelve_labs_video_id,
                type='summary'
            )

            summary = summary.summary

            return {
                'summary': summary
            }
        
        except Exception as e:

            raise Exception(f"Error generating summary: {str(e)}")
        
        
    async def generate_chapters(self):

        """
        
        Generates chapters for video according to data schema defined.

        If output from TwelveLabs provider cannot be validated against the data schema, it will be reformatted by reasoning model.
        
        """

        try:

            raw_chapters = await self._prompt_llm(prompt=prompts.chapter_prompt, data_schema=data_schema.ChaptersSchema)
            
            self.chapters = raw_chapters

            return raw_chapters

        
        except Exception as e:

            print(f"Error generating chapters: {str(e)}")
            return raw_chapters
        
    async def generate_key_takeaways(self):

        """
        
        Generates key takeaways for the video.
        
        """

        try:

            raw_key_takeaways = await self._prompt_llm(prompt=prompts.key_takeaways_prompt, data_schema=data_schema.KeyTakeawaysSchema)
            
            self.key_takeaways = raw_key_takeaways

            return raw_key_takeaways
        
        except Exception as e:

            print(f"Error generating key takeaways: {str(e)}")
            return raw_key_takeaways
        
    async def generate_pacing_recommendations(self):

        """
        
        Generates pacing recommendations for the video.
        
        """

        try:

            raw_pacing_recommendations = await self._prompt_llm(prompt=prompts.pacing_recommendations_prompt, data_schema=data_schema.PacingRecommendationsSchema)
            
            self.pacing_recommendations = raw_pacing_recommendations

            return raw_pacing_recommendations
        
        except Exception as e:

            print(f"Error generating pacing recommendations: {str(e)}")
            return raw_pacing_recommendations
        
        
    async def generate_quiz_questions(self, chapters: list):

        """
        
        Generates quiz questions for the video.
        
        """

        print(f"Chapters: {chapters}")

        # Validate that chapters is a list and not empty
        if not chapters or not isinstance(chapters, list) or len(chapters) == 0:
            raise Exception("Chapters must be a non-empty list")

        chapters_string = "\n".join([f"{chapter['title']}: {chapter['summary']}" for chapter in chapters])

        quiz_questions_prompt = prompts.quiz_questions_prompt.format(chapters=chapters_string)

        try:

            raw_quiz_questions = await self._prompt_llm(prompt=quiz_questions_prompt, data_schema=data_schema.QuizQuestionsSchema)
            
            self.quiz_questions = raw_quiz_questions

            return raw_quiz_questions
        
        except Exception as e:

            print(f"Error generating quiz questions: {str(e)}")
            return raw_quiz_questions
        
    async def generate_engagement(self):

        """

        Generates engagement for the video.
        
        """
        
        try:

            raw_engagement = await self._prompt_llm(prompt=prompts.engagement_prompt, data_schema=data_schema.EngagementListSchema)
            
            self.engagement = raw_engagement

            return raw_engagement
        
        except Exception as e:

            print(f"Error generating engagement: {str(e)}")
            return raw_engagement
        
    async def generate_gist(self):

        """
        
        Generates a gist of the video.
        
        """

        try: 

            gist = self.twelve_labs_client.gist(video_id=self.twelve_labs_video_id, types=['topic', 'hashtag', 'title'])

            title, hashtags, topics = gist.title, gist.hashtags, gist.topics

            self.title = title
            self.hashtags = hashtags
            self.topics = topics

            return {
                'title': title,
                'hashtags': hashtags,
                'topics': topics
            }

        except Exception as e:

            raise Exception(f"Error generating gist: {str(e)}")
    
__all__ = ["TwelveLabsHandler"]