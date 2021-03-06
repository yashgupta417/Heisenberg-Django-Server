from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .serializers import UserSerializer,QuestionSerializer,ContestSerializer,ParticipantSerializer,ContestMiniSerializer,QuestionMiniSerializer,UserMiniSerializer
from django.contrib.auth import get_user_model
from .models import Question,Contest,Participant
from django.db.models import Q
# Create your views here.
def IndexView(request):
    return HttpResponse("HeisenBerg.")

class SignupAPIView(generics.CreateAPIView):
    serializer_class=UserSerializer
    def get_queryset(self):
        return get_user_model().objects.all()

class UserListAPIView(generics.ListAPIView):
    serializer_class=UserMiniSerializer
    def get_queryset(self):
        query=self.request.query_params.get('q',None)
        if query!=None:
            return get_user_model().objects.filter(Q(username__icontains=query)|Q(first_name__icontains=query))
        return get_user_model().objects.all()

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=UserSerializer

    def get_queryset(self):
        return get_user_model().objects.all()

    def get_object(self):
        return get_user_model().objects.get(username=self.kwargs['username'])

class QuestionListAPIView(generics.ListCreateAPIView):
    serializer_class=QuestionMiniSerializer

    def get_queryset(self):
        return Question.objects.filter(is_available_for_practice=True)

class QuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=QuestionSerializer

    def get_queryset(self):
        return Question.objects.all()

    def get_object(self):
        return Question.objects.get(id=self.kwargs['id'])

class ContestListAPIView(generics.ListCreateAPIView):
    serializer_class=ContestSerializer

    def get_queryset(self):
        q=self.request.query_params.get('q','all')
        if q=='upcoming':
            return Contest.objects.filter(is_finished=False)
        elif q=='finished':
            return Contest.objects.filter(is_finished=True)
        return Contest.objects.all()

class ContestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=ContestSerializer

    def get_queryset(self):
        return Contest.objects.all()

    def get_object(self):
        return Contest.objects.get(id=self.kwargs['id'])

class ContestParticipantsAPIView(generics.ListAPIView):
    serializer_class=ParticipantSerializer

    def get_queryset(self):
        contest_id=self.kwargs['contest_id']
        return Participant.objects.filter(contest=contest_id).order_by('-score')

class UserAsParticipantsAPIView(generics.ListAPIView):
    serializer_class=ParticipantSerializer

    def get_queryset(self):
        username=self.kwargs['username']
        return Participant.objects.filter(user__username=username)

from rest_framework.views import APIView
from rest_framework.response import Response
class RegisterForContestAPIView(APIView):
    def post(self,request,*args,**kwargs):
        c_id=self.kwargs['contest_id']
        u_username=self.kwargs['user_username']
        contest=Contest.objects.get(id=c_id)
        user=get_user_model().objects.get(username=u_username)
        p=Participant.objects.create(contest=contest,user=user,intital_rating=user.rating)
        all_p=Participant.objects.filter(contest__id=c_id).order_by('-score')
        i=0
        j=0
        prev_score=10000000
        for p in all_p.iterator():
            if p.score<prev_score:
                i+=1+j
                j=0
            else:
                j+=1
            p.rank=i
            p.save()
            prev_score=p.score
        return Response({})

class SubmitAnswerAPIView(APIView):
    def post(self,request,*args,**kwargs):
        q_id=self.kwargs['q_id']
        p_id=self.kwargs['p_id']
        c_id=self.kwargs['c_id']
        answer=self.request.query_params.get('answer',None)
        if answer!=None:
            que=Question.objects.get(id=q_id)
            participant=Participant.objects.get(id=p_id)
            msg=''
            if participant not in que.solved_by.all():
                if que.answer==answer:
                    participant.score+=que.points
                    participant.questions_solved_count+=1
                    que.solved_by_count+=1
                    que.solved_by.add(participant)
                    participant.save()
                    que.save()
                    msg='Correct Answer'
                else:
                    participant.score-=50
                    participant.save()
                    msg='Wrong Answer'
                all_p=Participant.objects.filter(contest__id=c_id).order_by('-score')
                i=0
                j=0
                prev_score=10000000
                for p in all_p.iterator():
                    if p.score<prev_score:
                        i+=1+j
                        j=0
                    else:
                        j+=1
                    p.rank=i
                    p.save()
                    prev_score=p.score
            else:
                msg='Already Submitted Successfully'
        return Response({'message':msg})
