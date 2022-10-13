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

    # Many-to-many relationship with Exercise
    # coach_exercises = models.ManyToManyField(Exercise)


class Exercise(models.Model):
    
    id = models.AutoField(primary_key=True)
    # One-to-many relationship with Coach
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True)
    # coach_username = models.CharField(max_length=50)
    
    name = models.CharField(max_length=50)
    img = models.FileField(max_length=150, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return self.name





# class AppUser(models.Model):

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    # username = models.CharField(max_length=50, primary_key=True)
    # email = models.CharField(max_length=50)
    # password = models.CharField(max_length=50)
    # image = models.FileField()

    # def __str__(self):
        # self.username




class Trainee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Many-to-one relationship with Coach
    trainee_coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True)

    # Many-to-many relationship with Assigned_Exercise
    assigned_exercises = models.ManyToManyField(AssignedExercise)

    # One-to-many relationship with Report
    weight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)


class Report(models.Model):

    id = models.AutoField(primary_key=True)

    # Many-to-one relationship with Trainee
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    # Many-to-many relationship with Exercise
    exercises = models.ManyToManyField(Exercise)

    date = models.DateField()

    correctness = models.FloatField()
    performance = models.FloatField()
    improvement = models.FloatField()
    calories_burned = models.IntegerField()

    def __str__(self):
        return self.trainee.username + " - " + str(self.date)

# Extends Exercise
class AssignedExercise(Exercise):

    assigned_id = models.AutoField(primary_key=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    correctness = models.FloatField(default=0)
    performance = models.FloatField(default=0)
    improvement = models.FloatField(default=0)
    calories_burned = models.IntegerField(default=0)
    grade = models.IntegerField(default=0)
