from .llm import LLMProvider
from helpers import gist_prompt, chapter_prompt, key_takeaways_prompt, pacing_recommendations_prompt, quiz_questions_prompt, engagement_prompt, summary_prompt
from helpers import GistSchema, ChaptersSchema, KeyTakeawaysSchema, PacingRecommendationsSchema, QuizQuestionsSchema, EngagementListSchema, SummarySchema
from helpers import TranscriptSchema, multimodal_transcript_prompt
from helpers.reasoning import LectureBuilderAgent
import pydantic
import asyncio

from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class GoogleHandler(LLMProvider):

    def __init__(self, gemini_file_id: str):

        self.gemini_file_id = gemini_file_id
        self.reasoning_agent = LectureBuilderAgent()

    async def _prompt_llm(self, prompt: str, data_schema: pydantic.BaseModel):

        """

        Prompts the LLM with the given prompt and returns the response.

        """

        try:
            
            client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
             
            prompt_content = [
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_uri(
                            file_uri=self.gemini_file_id,
                            mime_type='video/mp4'
                        )
                    ]
                ),
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_text(
                            text=prompt
                        )
                    ]
                )
            ]

            response = await asyncio.to_thread(client.models.generate_content,
                model='models/gemini-2.5-flash-preview-05-20',
                contents=prompt_content,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': data_schema
                }
            )
       
            formatted_response : data_schema = response.parsed
            return formatted_response.model_dump()
        
        except pydantic.ValidationError as e:
            
            """
            response = await asyncio.to_thread(
                self.reasoning_agent.reformat_text,
                text=response.text,
                data_schema=data_schema
            )

            return response.model_dump()
            """

        except Exception as e:

            print(f"Error generating gist: {e}")
            return response

    async def generate_gist(self):
        
        """
        
        Generates a gist of the video using Google Gemini which includes:
        1. Title
        2. Hashtags
        3. Topics
        
        """

        try:
            
            response = await self._prompt_llm(prompt=gist_prompt, data_schema=GistSchema)

            return response

        except Exception as e:

            print(f"Error generating gist: {e}")
            return None
        
    async def generate_chapters(self):

        """
        
        Generates chapters of the video using Google Gemini.

        """

        try:

            response = await self._prompt_llm(prompt=chapter_prompt, data_schema=ChaptersSchema)

            return response
        
        except Exception as e:

            print(f"Error generating chapters: {e}")
            return None
        
    async def generate_key_takeaways(self):

        """
        
        Generates key takeaways of the video using Google Gemini.

        """

        try:

            response = await self._prompt_llm(prompt=key_takeaways_prompt, data_schema=KeyTakeawaysSchema)

            return response
        
        except Exception as e:

            print(f"Error generating key takeaways: {e}")
            return None
        
    async def generate_pacing_recommendations(self):

        """
        
        Generates pacing recommendations of the video using Google Gemini.

        """

        try:

            response = await self._prompt_llm(prompt=pacing_recommendations_prompt, data_schema=PacingRecommendationsSchema)

            return response
        
        except Exception as e:

            print(f"Error generating pacing recommendations: {e}")
            return None
        
    async def generate_quiz_questions(self, chapters: list):  

        """

        Generates quiz questions of the video using Google Gemini.

        """

        try:

            chapters_string = "\n".join([f"{chapter['title']}: {chapter['summary']}" for chapter in chapters])

            response = await self._prompt_llm(prompt=quiz_questions_prompt.format(chapters=chapters_string), data_schema=QuizQuestionsSchema)

            return response
        
        except Exception as e:

            print(f"Error generating quiz questions: {e}")
            return None
        
    async def generate_engagement(self):

        """

        Generates engagement of the video using Google Gemini.

        """

        try:

            response = await self._prompt_llm(prompt=engagement_prompt, data_schema=EngagementListSchema)

            return response
        
        except Exception as e:

            print(f"Error generating engagement: {e}")
            return None

    async def generate_summary(self):

        """
        
        Generates summary for the video using Google Gemini.
        
        """

        try:

            response = await self._prompt_llm(prompt=summary_prompt, data_schema=SummarySchema)

            return response

        except Exception as e:

            print(f"Error generating summary: {e}")
            return None
        
    async def generate_transcript(self):
        
        """
        
        Generates transcript for the video using Google Gemini.
        
        """

        try:
            
            response = await self._prompt_llm(prompt=multimodal_transcript_prompt, data_schema=TranscriptSchema)
            
            return response
        
        except Exception as e:

            print(f"Error generating transcript: {e}")
            return None

__all__ = ['GoogleHandler']