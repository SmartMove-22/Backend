from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)

    def __str__(self):
        return self.category + " - " + self.sub_category


class Coach(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # One-to-many relationship with Trainee

    # One-to-many relationship with Exercise


class Exercise(models.Model):

    id = models.AutoField(primary_key=True)

    # One-to-many relationship with Coach
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=50)
    image = models.CharField(max_length=150, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return str(self.id) + " - " + self.name


class Trainee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Many-to-one relationship with Coach
    trainee_coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True)

    # Many-to-many relationship with Assigned_Exercise

    # One-to-many relationship with Report

    weight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)


# Extends Exercise
class AssignedExercise(models.Model):

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    assigned_id = models.AutoField(primary_key=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    correctness = models.FloatField(default=0)
    performance = models.FloatField(default=0)
    improvement = models.FloatField(default=0)
    calories_burned = models.IntegerField(default=0)
    pacing = models.FloatField(default=0)
    bpms = models.IntegerField(default=0)
    grade = models.IntegerField(default=0)


class Report(models.Model):

    id = models.AutoField(primary_key=True)

    # Many-to-one relationship with Trainee
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    # Many-to-many relationship with Exercise
    exercises = models.ManyToManyField(AssignedExercise)

    date = models.DateField()

    correctness = models.FloatField(default=0)
    performance = models.FloatField(default=0)
    improvement = models.FloatField(default=0)
    calories_burned = models.IntegerField(default=0)

    def __str__(self):
        return self.trainee.username + " - " + str(self.date)


class RealTimeReport(models.Model):

    id = models.AutoField(primary_key=True)
    correctness = models.FloatField()
    progress = models.FloatField()
    finished_repetition = models.BooleanField()
    first_half = models.BooleanField()
    most_divergent_angle_landmark_first = models.IntegerField(),
    most_divergent_angle_landmark_middle = models.IntegerField(),
    most_divergent_angle_landmark_last = models.IntegerField(),
    most_divergent_angle_value = models.FloatField()
