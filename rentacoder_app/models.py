from django.contrib.auth.models import User
from django.db import models


class Technology(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "technology"


# A RentACoderUser can publish Projects and create JobOffers in Projects
class RentACoderUser(models.Model):
    name = models.CharField(max_length=100)
    technologies = models.ManyToManyField('Technology')



# A Project is created by a User and can offer one or more job openings
class Project(models.Model):
    description = models.TextField()
    user = models.ForeignKey('RentACoderUser')
    technologies = models.ManyToManyField('Technology')
    openings = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    # duration: calculated in days, weeks, months?

    class Meta:
        db_table = "project"

# Users can post JobOffers for a Project
class JobOffer(models.Model):
    project = models.ForeignKey('Project')
    coder = models.ForeignKey('RentACoderUser')
    money = models.IntegerField()
    hours = models.IntegerField()
    message = models.TextField()

    class Meta:
        db_table = "job_offer"