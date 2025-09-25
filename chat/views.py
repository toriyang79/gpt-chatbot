"""Streaming and chat views for the chat app."""

import json
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Conversation, Message

try:
    # OpenAI Python SDK (1.x)
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # gracefully handle import at runtime


@login_required
@csrf_exempt  # 초보 테스트 편의: 나중에 CSRF 토큰 처리로 바꿀 수 있어요.
def send_message_stream_ndjson(request):
    """
    NDJSON(줄마다 JSON 한 개) 형태로 스트리밍 전송.
    프런트는 fetch + ReadableStream으로 줄 단위 처리.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    user_message = (payload.get('message') or '').strip()
    conversation_id = payload.get('conversation_id')

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # 대화 불러오거나 새로 만들기
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        conversation = Conversation.objects.create(user=request.user)
        conversation.title = user_message[:50] + ("..." if len(user_message) > 50 else "")
        conversation.save()

    # 사용자 메시지 저장
    Message.objects.create(conversation=conversation, role='user', content=user_message)

    # OpenAI 요청 메시지 (시스템 프롬프트는 빈 문자열 권장사항 반영)
    messages_for_api = [{"role": "system", "content": ""}]
    for msg in conversation.messages.all():
        messages_for_api.append({"role": msg.role, "content": msg.content})

    # OpenAI 클라이언트 준비
    if OpenAI is None:
        return JsonResponse({'error': 'OpenAI SDK not available'}, status=500)
    client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))

    def line(obj: dict) -> str:
        return json.dumps(obj, ensure_ascii=False) + "\n"

    def stream_generator():
        full_chunks = []
        # 먼저 대화 ID를 한 줄로 알림(프런트가 새 대화 여부 처리 가능)
        yield line({"conversation_id": conversation.id})
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_api,
                stream=True,
            )
            for chunk in stream:
                try:
                    delta = getattr(chunk.choices[0].delta, "content", None)
                except Exception:
                    delta = None
                if delta:
                    full_chunks.append(delta)
                    yield line({"delta": delta})

            ai_text = "".join(full_chunks)
            Message.objects.create(conversation=conversation, role='assistant', content=ai_text)
            yield line({"done": True})
        except Exception as e:  # OpenAI/네트워크 에러 등
            yield line({"error": str(e)})

    response = StreamingHttpResponse(stream_generator(), content_type='application/x-ndjson; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


# 참고: 기존 SSE(EventSource)용 예시 핸들러(필요시 유지)
@login_required
@csrf_exempt
def send_message_stream(request):
    """
    SSE로 토막(청크) 단위 전송. (EventSource 전용)
    """
    try:
        user_message = (request.GET.get('message') or '').strip()
        conversation_id = request.GET.get('conversation_id')

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.create(user=request.user)
            conversation.title = user_message[:50] + ("..." if len(user_message) > 50 else "")
            conversation.save()

        Message.objects.create(conversation=conversation, role='user', content=user_message)

        messages_for_api = [{"role": "system", "content": ""}]
        for msg in conversation.messages.all():
            messages_for_api.append({"role": msg.role, "content": msg.content})

        if OpenAI is None:
            return JsonResponse({'error': 'OpenAI SDK not available'}, status=500)
        client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))

        def event_stream():
            full_chunks = []
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_api,
                    stream=True,
                )
                for chunk in stream:
                    delta = getattr(chunk.choices[0].delta, "content", None)
                    if delta:
                        full_chunks.append(delta)
                        yield f"data: {delta}\n\n"
                ai_text = "".join(full_chunks)
                Message.objects.create(conversation=conversation, role='assistant', content=ai_text)
                yield "event: done\ndata: [END]\n\n"
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream; charset=utf-8')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===== 기본 페이지 뷰들 =====
@login_required
def index(request):
    """대화 목록과 최근(또는 없음) 대화를 보여주는 기본 페이지."""
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    current_conversation = conversations.first() if conversations.exists() else None
    msgs = current_conversation.messages.all() if current_conversation else []
    return render(
        request,
        'chat/index.html',
        {
            'conversations': conversations,
            'current_conversation': current_conversation,
            'messages': msgs,
        },
    )


@login_required
def conversation_detail(request, conversation_id: int):
    """특정 대화를 선택해 같은 템플릿으로 렌더링."""
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    current_conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    msgs = current_conversation.messages.all()
    return render(
        request,
        'chat/index.html',
        {
            'conversations': conversations,
            'current_conversation': current_conversation,
            'messages': msgs,
        },
    )


@login_required
def new_chat(request):
    """새 대화를 만들고 그 대화 페이지로 이동."""
    if request.method != 'POST':
        return redirect('chat:index')
    conv = Conversation.objects.create(user=request.user, title='New Chat')
    return redirect('chat:conversation_detail', conversation_id=conv.id)


@login_required
@csrf_exempt
def send_message(request):
    """비스트리밍(레거시) 엔드포인트 자리표시자. 스트리밍 사용을 안내."""
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')
    return JsonResponse({'success': False, 'error': '스트리밍 엔드포인트를 사용하세요: /send-message-stream/'}, status=400)
