from pydantic import BaseModel
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Dependency Models
class VideoIdRequest(BaseModel):
    twelve_labs_video_id: str
    s3_key: str
    gemini_file_id: str

class VideoIdRequestSingleProvider(BaseModel):
    video_id: str
    provider: str

class FetchVideoIdsResponse(BaseModel):
    status: str = 'success'
    message: str = 'Video uploaded successfully'
    data: dict = {
        'twelve_labs_video_id': str,
        's3_key': str,
        'gemini_file_id': str
    }

class SuccessResponse(BaseModel):
    status: str = 'success'
    provider: str
    message: str
    duration: float = 0.0
    data: dict | list
    type: str

class DefaultResponse(BaseModel):
    status: str = 'error'
    message: str = 'Error'

async def get_video_id_from_request(request: Request, body: VideoIdRequest | None = None):

    """

    Safely extracts the video ID from the request body or query parameters.

    Returns VideoIdRequest object that contains the video ID, s3 key, and gemini file ID.

    """

    if request.method == 'GET':
        video_id = request.query_params.get('video_id')
        s3_key = request.query_params.get('s3_key')
        gemini_file_id = request.query_params.get('gemini_file_id')
        return VideoIdRequest(twelve_labs_video_id=video_id, s3_key=s3_key, gemini_file_id=gemini_file_id)
    elif request.method == 'POST':
        if not body:
            raise HTTPException(status_code=400, detail="body is required")
        video_id = body.twelve_labs_video_id
        s3_key = body.s3_key
        gemini_file_id = body.gemini_file_id
    else:
        raise HTTPException(status_code=405, detail="Method not allowed")
    
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")
    
    return VideoIdRequest(twelve_labs_video_id=video_id, s3_key=s3_key, gemini_file_id=gemini_file_id)

async def get_video_id_from_request_single_provider(request: Request, body: VideoIdRequestSingleProvider | None = None):

    """
    Safely extracts the video ID and provider from the request body or query parameters.

    Returns VideoIdRequestSingleProvider object that contains the video ID and provider.
    
    """

    if request.method == 'GET':
        video_id = request.query_params.get('video_id')
        provider = request.query_params.get('provider')
    else:
        raise HTTPException(status_code=405, detail="Method not allowed")

    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")
    
    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")
    
    return VideoIdRequestSingleProvider(video_id=video_id, provider=provider)


def success_response(data: dict, duration: float, message: str, provider: str, type: str) -> JSONResponse:

    """
    Returns a JSON response with the following keys:
    - **status**: 'success'
    - **provider**: provider
    - **message**: message
    - **duration**: duration
    - **data**: data
    - **type**: type
    """
    
    return JSONResponse({
        'status': 'success',
        'provider': provider,
        'message': message,
        'duration': duration,
        'data': data,
        'type': type,
    }, status_code=200)

def default_response(status: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse({
        'status': status,
        'message': message
    }, status_code=status_code)

__all__ = ['VideoIdRequest', 'VideoIdRequestSingleProvider', 'FetchVideoIdsResponse', 'get_video_id_from_request', 'get_video_id_from_request_single_provider', 'SuccessResponse', 'DefaultResponse']