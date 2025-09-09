import boto3
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DBHandler:

    def __init__(self):
        try:
            self.dynamodb = boto3.resource('dynamodb')
            self.s3_client = boto3.resource('s3')
            logger.info("DynamoDB resource created successfully")
        except Exception as e:
            logger.error(f"Error creating DynamoDB resource: {str(e)}")
            raise

    def upload_video_ids(self, twelve_labs_video_id: str, s3_key: str, gemini_file_id: str):

        """
        Uploads video IDs to DynamoDB.
        Each row will contain UID of each video in their respective providers and create empty rows for metadata for future AI inference outputs from each provider.
        """

        try:
            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')
            
            if not table_name:
                logger.error("DYNAMODB_TABLE_NAME environment variable not set")
                raise Exception("DYNAMODB_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            logger.info("DynamoDB table reference obtained")

            item = {
                'video_id': twelve_labs_video_id,
                's3_key': s3_key,
                'gemini_file_id': gemini_file_id,
                'created_at': boto3.dynamodb.types.Decimal(str(int(time.time()))),
            }
            
            logger.info(f"Preparing to upload item: {item}")

            response = table.put_item(Item=item)
            logger.info(f"DynamoDB put_item response: {response}")

            return response
        
        except Exception as e:
            logger.error(f"=== Error in upload_video_ids: {str(e)} ===")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Error uploading video IDs: {str(e)}")
        
    def fetch_video_ids(self, video_id: str):

        """
        
        Fetches video IDs from DynamoDB.
        
        """

        try:

            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_TABLE_NAME environment variable not set")
            
            table = self.dynamodb.Table(table_name)

            response = table.get_item(Key={'video_id': video_id})
            item = response.get('Item', {})

            gemini_file_id = item.get('gemini_file_id', None)
            s3_key = item.get('s3_key', None)

            return gemini_file_id, s3_key
        
        except Exception as e:
            logger.error(f"=== Error in fetch_video_ids: {str(e)} ===")
            raise e
        
    def upload_course_metadata(self, video_id: str, title: str, chapters: list, quiz_questions: list, key_takeaways: list, pacing_recommendations: list, summary: str, engagement: list, transcript: str, gemini_file_id: str, s3_key: str):
        
        """
        
        Uploads course metadata to DynamoDB.
        
        """

        try:

            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            item = {
                'video_id': video_id,
                'gemini_file_id': gemini_file_id,
                's3_key': s3_key,
                'summary': summary,
                'created_at': boto3.dynamodb.types.Decimal(str(int(time.time()))),
                'title': title,
                'chapters': chapters,
                'quiz_questions': quiz_questions,
                'key_takeaways': key_takeaways,
                'pacing_recommendations': pacing_recommendations,
                'engagement': engagement,
                'transcript': transcript
            }

            response = table.put_item(Item=item)

            return response
        
        except Exception as e:
            logger.error(f"=== Error in upload_course_metadata: {str(e)} ===")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Error uploading course metadata: {str(e)}")

    def get_published_courses(self):
        
        """
        
        Retrieves all published courses from DynamoDB.
        
        """

        try:

            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            logger.info("DynamoDB table reference obtained for getting published courses")

            # Scan the table to get all items
            response = table.scan()
            items = response.get('Items', [])

            logger.info(f"Retrieved {len(items)} published courses from DynamoDB")

            return items
        
        except Exception as e:
            logger.error(f"=== Error in get_published_courses: {str(e)} ===")
            raise e
        
    def fetch_course_metadata(self, video_id: str):

        """

        Fetches course metadata for a given video ID from DynamoDB.

        """

        try:

            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            logger.info("DynamoDB table reference obtained for fetching course metadata")

            response = table.get_item(Key={'video_id': video_id})
            item = response.get('Item', {})

            if not item:
                raise ValueError(f"No course metadata found for video ID: {video_id}")

            logger.info(f"Successfully fetched course metadata for video ID: {video_id}")

            return item
        
        except Exception as e:

            logger.error(f"=== Error in fetch_course_metadata: {str(e)} ===")
            raise e
        
    def save_student_reaction(self, video_id: str, reaction: dict):
        """
        Saves a student reaction to DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            
            # Get existing reactions or initialize empty list
            response = table.get_item(Key={'video_id': video_id})
            item = response.get('Item', {})
            
            existing_reactions = item.get('student_reactions', [])
            existing_reactions.append(reaction)
            
            # Update the item with new reaction
            update_response = table.update_item(
                Key={'video_id': video_id},
                UpdateExpression='SET student_reactions = :reactions',
                ExpressionAttributeValues={
                    ':reactions': existing_reactions
                }
            )

            logger.info(f"Successfully saved student reaction for video ID: {video_id}")
            return update_response

        except Exception as e:
            logger.error(f"=== Error in save_student_reaction: {str(e)} ===")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Error saving student reaction: {str(e)}")

    def get_student_reactions(self, video_id: str):
        """
        Retrieves all student reactions for a given video ID from DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_TABLE_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_TABLE_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)

            response = table.get_item(Key={'video_id': video_id})
            item = response.get('Item', {})

            if not item:
                raise ValueError(f"No course metadata found for video ID: {video_id}")

            student_reactions = item.get('student_reactions', [])

            return student_reactions

        except Exception as e:
            logger.error(f"=== Error in get_student_reactions: {str(e)} ===")
            raise e

    def save_wrong_answer(self, student_name: str, video_id: str, wrong_answer: dict):
        """
        Saves a student's wrong answer to DynamoDB for analysis.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)
            
            # Get existing wrong answers or initialize empty list
            response = table.get_item(Key={'student_name': student_name})
            item = response.get('Item', {})
            
            existing_wrong_answers = item.get(video_id + "_wrong_answers", [])
            existing_wrong_answers.append(wrong_answer)
            
            # Update the item with new wrong answer
            update_response = table.update_item(
                Key={'student_name': student_name},
                UpdateExpression='SET #wrong_answer_id = :wrong_answers',
                ExpressionAttributeValues={
                    ':wrong_answers': existing_wrong_answers
                },
                ExpressionAttributeNames={
                    '#wrong_answer_id': video_id + "_wrong_answers"
                }
            )

            logger.info(f"Successfully saved wrong answer for video ID: {video_id}")
            return update_response

        except Exception as e:
            logger.error(f"=== Error in save_wrong_answer: {str(e)} ===")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Error saving wrong answer: {str(e)}")
        
    def get_student_profile(self, student_name: str):
        """
        Retrieves a student's profile from DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')
            
            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")
            
            table = self.dynamodb.Table(table_name)
            
            response = table.get_item(Key={'student_name': student_name})
            item = response.get('Item', {})

            if not item:
                raise ValueError(f"No student profile found for student name: {student_name}")
            
            return item
        
        except Exception as e:
            logger.error(f"=== Error in get_student_profile: {str(e)} ===")
            raise e
        
    async def save_student_progress_report(self, student_name: str, video_id: str, progress_report: dict):
        """
        Saves a student's progress report to DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')
            
            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")
            
            table = self.dynamodb.Table(table_name)
            
            response = table.update_item(
                Key={'student_name': student_name},
                UpdateExpression='SET #progress_report_id = :progress_report',
                ExpressionAttributeValues={
                    ':progress_report': progress_report
                },
                ExpressionAttributeNames={
                    '#progress_report_id': video_id + "_progress_report"
                }
            )

            logger.info(f"Successfully saved student progress report for video ID: {video_id}")
            return response
        
        except Exception as e:
            logger.error(f"=== Error in save_student_progress_report: {str(e)} ===")
            raise e

    def convert_progress_report_data_types(self, progress_report):
        """
        Converts progress report data from strings back to appropriate data types.
        """
        if not progress_report:
            return progress_report
            
        try:
            # Create a copy to avoid modifying the original
            converted_report = progress_report.copy()
            
            # Convert concept mastery data
            if 'concept_mastery' in converted_report and 'concept_mastery' in converted_report['concept_mastery']:
                for concept in converted_report['concept_mastery']['concept_mastery']:
                    if 'mastery_level' in concept and isinstance(concept['mastery_level'], str):
                        try:
                            concept['mastery_level'] = int(concept['mastery_level'])
                        except (ValueError, TypeError):
                            # If conversion fails, keep as string but log
                            print(f"Could not convert mastery_level '{concept['mastery_level']}' to int")
            
            # Convert accuracy if it's a string
            if 'accuracy' in converted_report and isinstance(converted_report['accuracy'], str):
                try:
                    converted_report['accuracy'] = float(converted_report['accuracy'])
                except (ValueError, TypeError):
                    print(f"Could not convert accuracy '{converted_report['accuracy']}' to float")
            
            # Convert total_questions if it's a string
            if 'total_questions' in converted_report and isinstance(converted_report['total_questions'], str):
                try:
                    converted_report['total_questions'] = int(converted_report['total_questions'])
                except (ValueError, TypeError):
                    print(f"Could not convert total_questions '{converted_report['total_questions']}' to int")
            
            print("Progress report data types converted successfully")
            return converted_report
            
        except Exception as e:
            print(f"Error converting progress report data types: {e}")
            return progress_report

    def fetch_student_progress_report(self, student_name: str, video_id: str):
        """
        Fetches a student's progress report from DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')
            
            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")
            
            table = self.dynamodb.Table(table_name)
            
            print(f"Searching for student: '{student_name}' and video_id: '{video_id}'")
            
            response = table.get_item(Key={'student_name': student_name})
            item = response.get('Item', {})

            # Check if the student item exists first
            if not item:
                print(f"No student profile found for student name: {student_name}")
                return None

            print(f"Found student profile for: {student_name}")
            print(f"Available keys in student profile: {list(item.keys())}")

            progress_report_key = video_id + "_progress_report"
            print(f'Looking for progress report with key: "{progress_report_key}"')
            
            progress_report = item.get(progress_report_key, None)
            print(f"Progress report value: {progress_report}")

            # Check if the specific progress report exists
            if not progress_report:
                print(f"No progress report found for video_id: {video_id} and student: {student_name}")
                print(f"Available progress report keys: {[key for key in item.keys() if key.endswith('_progress_report')]}")
                
                # Let's also check if there are any keys that contain the video_id
                matching_keys = [key for key in item.keys() if video_id in key]
                print(f"Keys containing video_id '{video_id}': {matching_keys}")
                
                return None
            
            print(f"Found progress report for {student_name} and {video_id}")
            
            # Convert data types before returning
            converted_progress_report = self.convert_progress_report_data_types(progress_report)
            return converted_progress_report
        
        except Exception as e:
            logger.error(f"=== Error in fetch_student_progress_report: {str(e)} ===")
            raise e
        
    def fetch_finished_videos(self, student_name: str):
        """
        Fetches all finished videos for a student from DynamoDB.
        """
        try:
            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')
            
            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")
            
            table = self.dynamodb.Table(table_name)
            
            response = table.get_item(Key={'student_name': student_name})
            item = response.get('Item', {})

            finished_videos = []

            for key, value in item.items():
                if key.endswith('_progress_report'):
                    finished_videos.append(key.replace('_progress_report', ''))

            return finished_videos
        
        except Exception as e:
            logger.error(f"=== Error in fetch_finished_videos: {str(e)} ===")
            raise e
        
    def fetch_student_data_from_course(self, video_id: str):
        
        """
        
        Fetches all student data from a course from DynamoDB.
        
        """

        try:

            table_name = os.getenv('DYNAMODB_CONTENT_USER_NAME')

            if not table_name:
                raise Exception("DYNAMODB_CONTENT_USER_NAME environment variable not set")

            table = self.dynamodb.Table(table_name)

            response = table.scan()

            items = response.get('Items', [])

            return items
        
        except Exception as e:
            logger.error(f"=== Error in fetch_student_data_from_course: {str(e)} ===")
            raise e
        
    def fetch_s3_presigned_urls(self):

        """
        
        Fetches all videos from the S3 storage bucket
        
        """

        try:

            presigned_urls = []

            for obj in boto3.client('s3').list_objects(Bucket=os.getenv('S3_BUCKET_NAME'))['Contents']:
                presigned_url = boto3.client('s3').generate_presigned_url('get_object', Params={'Bucket': os.getenv('S3_BUCKET_NAME'), 'Key': obj['Key']}, ExpiresIn=3600)
                presigned_urls.append(presigned_url)

            return presigned_urls
        
        except Exception as e:
            
            raise Exception(f"Error fetching S3 presigned URLs: {str(e)}")
        
__all__ = ['DBHandler']