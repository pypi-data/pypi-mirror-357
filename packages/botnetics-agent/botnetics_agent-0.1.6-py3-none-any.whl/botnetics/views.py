from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
from .models import Message, Attachment
from .app import get_current_app

@csrf_exempt
@require_http_methods(["POST"])
def message_endpoint(request):
    try:
        data = json.loads(request.body)
        
        # Extract authorization token from headers
        auth_header = request.headers.get('Authorization', '')
        callback_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        
        # Parse attachments from incoming data
        attachments = []
        for attachment_data in data.get('attachments', []):
            attachment = Attachment(
                type=attachment_data.get('type', ''),
                filename=attachment_data.get('filename', ''),
                url=attachment_data.get('url', ''),
                mime_type=attachment_data.get('mime_type'),
                size_bytes=attachment_data.get('size_bytes')
            )
            attachments.append(attachment)
        
        # Create Message object from incoming data
        message = Message(
            text=data.get('text', ''),
            chat_id=data.get('chat_id', ''),
            user_id=data.get('user_id', ''),
            attachments=attachments
        )
        
        # Get current app and run handlers
        app = get_current_app()
        if app and app.message_handlers:
            response = app.message_handlers[0](message)
            
            # Debug: Print what we received and what we're sending
            print(f"[DEBUG] Received {len(message.attachments)} attachments")
            for i, att in enumerate(message.attachments):
                print(f"[DEBUG] Attachment {i}: {att.filename}, {att.url}")
            
            print(f"[DEBUG] Response type: {type(response)}")
            print(f"[DEBUG] Response has attachments attr: {hasattr(response, 'attachments')}")
            if hasattr(response, 'attachments'):
                print(f"[DEBUG] Response attachments: {len(response.attachments) if response.attachments else 0}")
            
            # Send response back to Botnetics callback endpoint
            callback_url = "https://botnetics.fly.dev/api/agent/callback"
            
            # Prepare attachments for callback to match Elixir controller format
            callback_attachments = []
            if hasattr(response, 'attachments') and response.attachments:
                for attachment in response.attachments:
                    callback_attachments.append({
                        "url": attachment.url,
                        "filename": attachment.filename,
                        "type": attachment.type,
                        "mime_type": attachment.mime_type,
                        "size_bytes": attachment.size_bytes
                    })
            
            print(f"[DEBUG] Callback attachments: {len(callback_attachments)}")
            print(f"[DEBUG] Callback payload attachments: {callback_attachments}")
            
            callback_payload = {
                "text": response.text,
                "chat_id": data.get('chat_id', ''),
                "attachments": callback_attachments
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