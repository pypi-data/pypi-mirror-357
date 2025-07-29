from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
from .models import Message
from .app import get_current_app

@csrf_exempt
@require_http_methods(["POST"])
def message_endpoint(request):
    try:
        data = json.loads(request.body)
        
        # Extract authorization token from headers
        auth_header = request.headers.get('Authorization', '')
        callback_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        
        # Create Message object from incoming data
        message = Message(
            text=data.get('text', ''),
            chat_id=data.get('chat_id', ''),
            user_id=data.get('user_id', ''),
            attachments=[]
        )
        
        # Get current app and run handlers
        app = get_current_app()
        if app and app.message_handlers:
            response = app.message_handlers[0](message)
            
            # Send response back to Botnetics callback endpoint
            callback_url = "https://botnetics.fly.dev/api/agent/callback"
            
            callback_payload = {
                "text": response.text,
                "chat_id": data.get('chat_id', '')
                # Add attachments if needed in the future
            }
            
            callback_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {callback_token}"
            }
            
            # Send the response back to Botnetics
            callback_response = requests.post(
                callback_url, 
                json=callback_payload,
                headers=callback_headers
            )
            
            # Log the callback response status
            callback_status = "success" if callback_response.status_code == 200 else "error"
            
            return JsonResponse({
                "status": "success",
                "callback_status": callback_status,
                "response": {
                    "text": response.text,
                    "attachments": [att.__dict__ for att in response.attachments]
                }
            })
        
        return JsonResponse({"status": "success", "message": "No handlers registered"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)