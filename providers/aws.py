from .llm import LLMProvider
from helpers import gist_prompt, chapter_prompt, key_takeaways_prompt, pacing_recommendations_prompt, quiz_questions_prompt, engagement_prompt, summary_prompt, ChaptersSchema
from helpers import KeyTakeawaysSchema, SummarySchema, TranscriptSchema, multimodal_transcript_prompt, GistSchema
from helpers import PacingRecommendationsSchema
from helpers import QuizQuestionsSchema
from helpers import EngagementListSchema
from helpers.reasoning import LectureBuilderAgent
import os
from dotenv import load_dotenv
import json
import asyncio
import boto3
import pydantic
from pydantic_core import from_json

load_dotenv(override=True)

class AWSHandler(LLMProvider):

    def __init__(self, s3_key: str):

        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.bedrock_model_id = 'amazon.nova-lite-v1:0'

        self.reasoning_agent = LectureBuilderAgent()

        self.s3_key = s3_key
        self.s3_file_name = 's3://' + os.getenv('S3_BUCKET_NAME') + '/' + self.s3_key

    async def _prompt_llm(self, prompt: str, data_schema: pydantic.BaseModel):

        """ Prompts the LLM with the given prompt and returns the response. """

        try:

            message_list = [
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mp4",
                                "source": {
                                    "s3Location": {
                                        "uri": self.s3_file_name, 
                                        "bucketOwner": os.getenv('AWS_ACCOUNT_ID')
                                    }
                                }
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ]

            # Note: This is the only way to get the model to return a JSON object.
            inference_config = {
                "topP": 1,
                "topK": 1,
                "temperature": 0,
            }

            native_request = {
                "messages": message_list,
                "inferenceConfig": inference_config
            }

            response = await asyncio.to_thread(self.bedrock_client.invoke_model,
                modelId=self.bedrock_model_id,
                body=json.dumps(native_request)
            )

            original_response = json.loads(response.get('body').read())
            model_response = original_response['output']['message']['content'][0]['text']
            model_response = model_response.replace("```json", "").replace("```", "")
            model_response = data_schema.model_validate_json(from_json(json.dumps(model_response), allow_partial=True))

            return model_response.model_dump()
        
        except pydantic.ValidationError as e:

            agent = LectureBuilderAgent()
            response = agent.reformat_text(text=original_response, data_schema=data_schema)

            return response.model_dump()
           
        except Exception as e:

            print(f"Error generating gist: {e}")
            return response

    async def generate_gist(self):
        
        """
        
        Generates a gist of the video using AWS Bedrock.

        The gist should include:
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
        
        """ Generates chapters of the video using AWS Bedrock. """

        try:
            response = await self._prompt_llm(prompt=chapter_prompt, data_schema=ChaptersSchema)
            return response
        except Exception as e:
            print(f"Error generating chapters: {e}")
            return None

    async def generate_key_takeaways(self):
        
        """ Generates key takeaways of the video using AWS Bedrock. """

        try:
            response = await self._prompt_llm(prompt=key_takeaways_prompt, data_schema=KeyTakeawaysSchema)
            return response
        except Exception as e:
            print(f"Error generating key takeaways: {e}")
            return None
    
    async def generate_pacing_recommendations(self):
        
        """ Generates pacing recommendations of the video using AWS Bedrock. """

        try:
            response = await self._prompt_llm(prompt=pacing_recommendations_prompt, data_schema=PacingRecommendationsSchema)
            return response
        except Exception as e:
            print(f"Error generating pacing recommendations: {e}")
            return None
        
    async def generate_quiz_questions(self, chapters: list):
        
        """ Generates quiz questions of the video using AWS Bedrock. """     

        try:
            chapters_string = "\n".join([f"{chapter['title']}: {chapter['summary']}" for chapter in chapters])
            response = await self._prompt_llm(prompt=quiz_questions_prompt.format(chapters=chapters_string), data_schema=QuizQuestionsSchema)
            return response
        except Exception as e:
            print(f"Error generating quiz questions: {e}")
            return None
        
    async def generate_engagement(self):

        """
        
        Generates engagement of the video using AWS Bedrock.

        """

        try:

            response = await self._prompt_llm(prompt=engagement_prompt, data_schema=EngagementListSchema)

            return response
        
        except Exception as e:

            print(f"Error generating engagement: {e}")
            return None
        
    async def generate_summary(self):
        
        """
        
        Generates summary for the video using AWS Bedrock.
        
        """

        try:

            response = await self._prompt_llm(prompt=summary_prompt, data_schema=SummarySchema)

            return response

        except Exception as e:

            print(f"Error generating summary: {e}")
            return None
        
    async def generate_transcript(self):

        """
        
        Generates transcript for the video using AWS Bedrock.
        
        """

        try:
            
            response = await self._prompt_llm(prompt=multimodal_transcript_prompt, data_schema=TranscriptSchema)
            
            return response
        
        except Exception as e:

            print(f"Error generating transcript: {e}")
            return None


__all__ = ['AWSHandler']