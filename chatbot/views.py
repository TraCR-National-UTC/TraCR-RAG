from django.shortcuts import render, redirect
from django.http import JsonResponse
from .tracr_rag import get_response, create_query_engines
import time

state_wise_query_engines = create_query_engines()

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