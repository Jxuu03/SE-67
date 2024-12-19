from django.db import models
from django.contrib.auth.models import User

# Member Model
class Member(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    deviceToken = models.CharField(max_length=255, null=True, blank=True)  
    eventOwned = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='event_owners', null=True, blank=True)  
    eventJoined = models.ManyToManyField('Event', related_name='event_participants', blank=True)  
    eventJoinedNotiEnabled = models.JSONField(default=dict, blank=True)  

    def __str__(self):
        return f"{self.username} ({self.email})"


# Event Model
class Event(models.Model):
    eventOwnerID = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='owned_events')
    eventName = models.CharField(max_length=255)
    eventDescription = models.TextField()
    eventDate = models.DateTimeField()
    eventLocation = models.CharField(max_length=255)
    eventStatus = models.CharField(max_length=50, 
                                   choices=[('Upcoming', 'Upcoming'), 
                                            ('Ongoing', 'Ongoing'), 
                                            ('Completed', 'Completed')], default='Upcoming')
    joinedMember = models.ManyToManyField(Member, related_name='events_joined', blank=True)
    
    def __str__(self):
        return self.eventName


# Post Model
class Post(models.Model):
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='posts')
    postOwnerID = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='posts_created')
    postTitle = models.CharField(max_length=255)
    postContent = models.TextField()
    postDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.postTitle} - {self.eventID.eventName}"


# Notification Model
class Notification(models.Model):
    eventID = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    recipientID = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notiTitle = models.CharField(max_length=255)
    notiContent = models.TextField()
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Failed', 'Failed'), ('Pending', 'Pending')], default='Pending')

    def __str__(self):
        return f"{self.notiTitle} - {self.eventID.eventName}"
