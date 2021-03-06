from .models import User,Question,Contest,Participant
from rest_framework import serializers
from django.contrib.auth import get_user_model


class ParticipantSerializer(serializers.ModelSerializer):
    #contest=ContestMiniSerializer(read_only=True)
    #questions_solved=Question(many=True,read_only=True)
    class Meta():
        model=Participant
        fields='__all__'
        depth=1

class ParticipantMiniSerializer(serializers.ModelSerializer):
    class Meta():
        model=Participant
        exclude=['user']
        depth=1
class UserSerializer(serializers.ModelSerializer):
    as_participant=ParticipantMiniSerializer(many=True,read_only=True)
    class Meta():
        model=get_user_model()
        fields='__all__'

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta():
        model=get_user_model()
        fields='__all__'

class QuestionMiniSerializer(serializers.ModelSerializer):
    class Meta():
        model=Question
        exclude=['solved_by']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta():
        model=Question
        fields='__all__'
        depth=1

class ContestMiniSerializer(serializers.ModelSerializer):
    class Meta():
        model=Contest
        fields='__all__'



class ContestSerializer(serializers.ModelSerializer):
    #participants=ParticipantSerializer(many=True,read_only=True)
    questions=QuestionMiniSerializer(many=True,read_only=True)
    class Meta():
        model=Contest
        fields='__all__'
        depth=1
