from django.db import models


class Category(models.Model):

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)

    def __str__(self):
        return self.name + " - " + self.sub_category


class Exercise(models.Model):

    id = models.AutoField(primary_key=True)
    # One-to-many relationship with Coach
    name = models.CharField(max_length=50, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return self.name


# Extends Exercise
class AssignedExercise(Exercise):

    # Many-to-many relationship with Trainee
    completed = models.BooleanField(default=False)
    correctness = models.FloatField(default=0)
    performance = models.FloatField(default=0)
    improvement = models.FloatField(default=0)
    calories_burned = models.IntegerField(default=0)
    grade = models.IntegerField(default=0)


class User(models.Model):

    username = models.CharField(max_length=50, primary_key=True)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/', default='images/default.jpg')

    weight = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    def __str__(self):
        return self.username


# Extends User
class Trainee(User):

    # Many-to-one relationship with Coach
    coach = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # Many-to-many relationship with Assigned_Exercise
    assigned_exercises = models.ManyToManyField(AssignedExercise, null=True)

    # One-to-many relationship with Report


# Extends User
class Coach(User):

    # One-to-many relationship with Trainee

    # Many-to-many relationship with Assigned_Exercise
    assigned_exercises = models.ManyToManyField(AssignedExercise, null=True)

    # Many-to-many relationship with Exercise
    available_exercises = models.ManyToManyField(Exercise, null=True)


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


class RealTimeReport(models.Model):

    id = models.AutoField(primary_key=True)
    correctness = models.FloatField()
    progress = models.FloatField()
    repetition = models.IntegerField()
    repetition_half = models.IntegerField()
