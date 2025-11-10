from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.views.decorators.http import condition
import json
from .tracr_rag import get_response, create_query_engines, get_response_streamed
import time
##
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from time import time as _time

# Simple in-memory cache to remember recently completed SSE sids.
# Format: { sid_str: { 'status': 'done', 'ts': timestamp } }
_sse_sessions = {}

##


# state_wise_query_engines = create_query_engines()

# Create your views here.
def chatbot_titan(request):
    # sol()
    # chats = Chat.objects.filter(user=request.user)

    print('Chat bot titan')
    if request.method == 'POST':
        query = request.POST.get('message')
        # print(message)
        start_time = time.time()
        response = get_response(query=query)
        end_time = time.time()
        processing_time = end_time - start_time
        print('titan', processing_time)

        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()
        return JsonResponse({'message': query, 'response': response})
    return render(request, 'chatbot/chatbot.html')



## ---------------------------------------------------------------------------------------
def index(request):
    # Render the main chat UI
    html = render_to_string("chatbot/index.html", {})
    return HttpResponse(html)

@csrf_exempt
def api_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_msg = (data.get("message") or "").strip()
        if not user_msg:
            return JsonResponse({"error": "Empty message"}, status=400)

        # --- Option A: Simple demo response (no external APIs) ---
        answer = demo_answer(user_msg)

        # --- Option B: Call your Spark backend here instead ---
        # answer = call_your_spark(user_msg)

        # --- Option C: Use OpenAI server-side (never expose key to browser) ---
        # if OPENAI_API_KEY:
        #     answer = call_openai(user_msg)
        # else:
        #     answer = demo_answer(user_msg)

        return JsonResponse({"answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def demo_answer(msg: str) -> str:
    # Very basic placeholder; replace with your logic
    tokens = msg.split()
    long_string_1 = '''Harry Potter and the Philosopher's Stone (also known as Harry Potter and the Sorcerer's Stone in the United States, India, and the Philippines) is a 2001 fantasy film directed by Chris Columbus and written by Steve Kloves, based on the 1997 novel by J. K. Rowling. It is the first instalment in the Harry Potter film series, and stars Daniel Radcliffe as Harry Potter, with Rupert Grint as Ron Weasley, and Emma Watson as Hermione Granger. Its story follows Harry's first year at Hogwarts School of Witchcraft and Wizardry as he discovers that he is a famous wizard and begins his formal wizarding education.'''
    long_string_2 = '''Warner Bros. Pictures bought the film rights to the book in 1999 for a reported £1 million ($1.65 million). Production began in the United Kingdom in 2000, with Columbus being chosen to helm the film from a short list of directors that included Steven Spielberg and Rob Reiner. Rowling insisted that the entire cast be British and Irish, with the three leads chosen in August 2000 following open casting calls. Filming took place at Leavesden Film Studios and historic buildings around the United Kingdom from September 2000 to March 2001.'''
    long_string_3 = '''Harry Potter and the Philosopher's Stone was previewed for two days in cinemas in the United Kingdom from 10 November 2001, and opened on 16 November in both the United Kingdom and the United States. It became a critical and commercial success, grossing $974 million at the box office during its initial run and over $1 billion with subsequent re-releases, against a $125 million budget. It became the highest-grossing film of 2001 and the second-highest-grossing film at the time. The film was nominated for several awards, including Academy Awards for Best Original Score, Best Art Direction and Best Costume Design. It was followed by seven sequels, beginning with Harry Potter and the Chamber of Secrets in 2002 and ending with Harry Potter and the Deathly Hallows – Part 2 in 2011.'''

    long_string = long_string_1 + "\n\n" + long_string_2 + "\n\n" + long_string_3
    return long_string

def demo_answer_parts(msg: str) -> str:
    # Very basic placeholder; replace with your logic
    # long_string_1 = '''# Part 1: 
    # Harry Potter and the Philosopher's Stone (also known as Harry Potter and the Sorcerer's Stone in the United States, India, and the Philippines) is a 2001 fantasy film directed by Chris Columbus and written by Steve Kloves, based on the 1997 novel by J. K. Rowling. It is the first instalment in the Harry Potter film series, and stars Daniel Radcliffe as Harry Potter, with Rupert Grint as Ron Weasley, and Emma Watson as Hermione Granger. Its story follows Harry's first year at Hogwarts School of Witchcraft and Wizardry as he discovers that he is a famous wizard and begins his formal wizarding education.\n\n'''
    # long_string_2 = '''## Part 2: 
    # Warner Bros. Pictures bought the film rights to the book in 1999 for a reported £1 million ($1.65 million). Production began in the United Kingdom in 2000, with Columbus being chosen to helm the film from a short list of directors that included Steven Spielberg and Rob Reiner. Rowling insisted that the entire cast be British and Irish, with the three leads chosen in August 2000 following open casting calls. Filming took place at Leavesden Film Studios and historic buildings around the United Kingdom from September 2000 to March 2001.\n\n'''
    # long_string_3 = '''### Part 3: 
    # Harry Potter and the Philosopher's Stone was previewed for two days in cinemas in the United Kingdom from 10 November 2001, and opened on 16 November in both the United Kingdom and the United States. It became a critical and commercial success, grossing $974 million at the box office during its initial run and over $1 billion with subsequent re-releases, against a $125 million budget. It became the highest-grossing film of 2001 and the second-highest-grossing film at the time. The film was nominated for several awards, including Academy Awards for Best Original Score, Best Art Direction and Best Costume Design. It was followed by seven sequels, beginning with Harry Potter and the Chamber of Secrets in 2002 and ending with Harry Potter and the Deathly Hallows – Part 2 in 2011.\n\n'''

    # short_string_1 = "This is a demo streamed response 1.\n\n"
    # short_string_2 = "This is a demo streamed response 2.\n\n"
    # short_string_3 = "This is a demo streamed response 3.\n\n"

    # time.sleep(1)
    # yield short_string_1
    # time.sleep(1)
    # yield short_string_2
    # time.sleep(1)
    # yield short_string_3
    # time.sleep(1)
    # yield long_string_1
    # time.sleep(1)
    # yield long_string_2
    # time.sleep(1)
    # yield long_string_3
    # time.sleep(1)
    # yield short_string_1
    # time.sleep(1)
    # yield short_string_2
    # time.sleep(1)
    # yield short_string_3
    # time.sleep(1)
    # yield long_string_1
    # time.sleep(1)
    # yield long_string_2
    # time.sleep(1)
    # yield long_string_3
    from urllib.parse import quote

    raw_1 = "/static/legislations/Current Cybersecurity Law/Alabama/Data Breach Notification Act/Files(12).pdf"
    raw = "/static/legislations/Current Cybersecurity Law/Alabama/Data Breach Notification Act/demo(a).pdf"
    safe_url_1 = quote(raw_1, safe="/:")  # encode spaces, parentheses, etc., but keep slashes
    safe_url_1 = safe_url_1.replace("(", "%28").replace(")", "%29")
    # md = f"[PDF]({safe_url})"
    safe_url_2 = quote("/static/legislations/Current Cybersecurity Law/demo.pdf", safe="/:")
    safe_url_3 = quote("/static/legislations/demo.pdf", safe="/:")

    # safe_url_4 = md_static_link(raw_1)



    demo_markdown = f"""
## 👋 Hi, I’m **TraCR-AI**

I’m your AI companion to help you with _Transportation Cybersecurity Legislations_.

---

### 🔍 Here’s what I can do:
- Summarize cybersecurity laws by state  
- Compare legislations between **Texas**, **Alabama**, and **South Carolina**  
- Provide quick references to important sections  

---

### 📚 Example:
> **Texas** defines *computer tampering* under [Texas Penal Code §33.02](https://statutes.capitol.texas.gov/Docs/PE/htm/PE.33.htm).

```python
# Example code block
print("Cybersecurity matters!")
print("Cybersecurity matters!")

print("Cybersecurity matters!")

print("Cybersecurity matters!")

print("Cybersecurity matters!")

print("Cybersecurity matters!")

print("Cybersecurity matters!")

```
[PDF3]({safe_url_3})
[PDF2]({safe_url_2})
[PDF1]({safe_url_1})

"""
    yield demo_markdown

    # return get_response_streamed(query=msg)

def _sse(msg: str):
    # EventSource expects "data: ...\n\n" per message
    return f"data: {json.dumps({'delta': msg})}\n\n"

@condition(etag_func=None)
def api_chat_stream(request):
    user_msg = (request.GET.get("message") or "").strip()
    # DEBUG: log incoming stream requests to help identify reconnects/duplicates
    try:
        sid = request.GET.get('sid')
        remote = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')
        last_event_id = request.META.get('HTTP_LAST_EVENT_ID')
        print(f"[api_chat_stream] sid={sid} remote={remote} ua={ua} msg_len={len(user_msg)}")
        if last_event_id:
            print(f"[api_chat_stream] Last-Event-ID={last_event_id}")
    except Exception:
        print("[api_chat_stream] logging failed")
    if not user_msg:
        return HttpResponseBadRequest("Missing ?message=...")

    # If the same sid already completed recently, short-circuit and return an immediate 'done'
    if sid:
        sess = _sse_sessions.get(sid)
        if sess and sess.get('status') == 'done' and (_time() - sess.get('ts', 0) < 300):
            print(f"[api_chat_stream] replay short-circuit for sid={sid}")
            def short():
                yield "retry: 600000\n\n"
                yield "id: done\n"
                yield "event: done\ndata: {}\n\n"
            resp = StreamingHttpResponse(short(), content_type="text/event-stream")
            resp["Cache-Control"] = "no-cache, no-store"
            resp["X-Accel-Buffering"] = "no"
            return resp

    def stream():
        # discourage auto-reconnects (10 minutes)
        yield "retry: 600000\n\n"

        print(f"[api_chat_stream.stream] start sid={request.GET.get('sid')} msg_preview={user_msg[:80]}")

        for i, part in enumerate(demo_answer_parts(user_msg)):
            yield f"id: {i}\n"
            yield _sse(part)

        # explicit completion
        yield "id: done\n"
        yield "event: done\ndata: {}\n\n"
        print(f"[api_chat_stream.stream] done sid={request.GET.get('sid')}")
        # mark this sid as completed (so reconnects won't re-run heavy work)
        try:
            s = request.GET.get('sid')
            if s:
                _sse_sessions[s] = {'status': 'done', 'ts': _time()}
        except Exception:
            pass

    resp = StreamingHttpResponse(stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache, no-store"
    resp["X-Accel-Buffering"] = "no"
    return resp